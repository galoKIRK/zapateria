from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from .decorators import rol_requerido
from .models import Producto, Cliente, Proveedor, Venta, DetalleVenta, Compra, DetalleCompra, Usuario
import random
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import Venta, DetalleVenta
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm
from .models import Venta, DetalleVenta
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import Venta, DetalleVenta
from .models import Compra, DetalleCompra
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Compra, DetalleCompra
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Cliente

def login_view(request):
    """Vista de Login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Bienvenido {user.get_full_name() or user.username}!')
                
                # Redirigir a la página solicitada o al dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    
    return render(request, 'pos/login.html', {'form': form})

def logout_view(request):
    """Vista de Logout"""
    username = request.user.username
    auth_logout(request)
    messages.success(request, f'Hasta pronto {username}!')
    return redirect('login')


@login_required
def dashboard(request):
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0)
    
    # Estadísticas generales
    total_productos = Producto.objects.filter(activo=True).count()
    productos_bajo_stock = Producto.objects.filter(
        activo=True, 
        stock__lte=F('stock_minimo')
    ).count()
    
    # Ventas del día
    ventas_hoy = Venta.objects.filter(fecha__date=hoy.date())
    total_ventas_hoy = ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0
    cantidad_ventas_hoy = ventas_hoy.count()
    
    # Ventas del mes
    ventas_mes = Venta.objects.filter(fecha__gte=inicio_mes)
    total_ventas_mes = ventas_mes.aggregate(Sum('total'))['total__sum'] or 0
    
    # Productos más vendidos (últimos 30 días)
    hace_30_dias = hoy - timedelta(days=30)
    productos_vendidos = DetalleVenta.objects.filter(
        venta__fecha__gte=hace_30_dias
    ).values('producto__nombre', 'producto__marca').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    # Clientes recientes
    clientes_recientes = Cliente.objects.order_by('-fecha_registro')[:5]
    
    context = {
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'total_ventas_hoy': total_ventas_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'total_ventas_mes': total_ventas_mes,
        'productos_vendidos': productos_vendidos,
        'clientes_recientes': clientes_recientes,
    }
    return render(request, 'pos/dashboard.html', context)

@login_required
def productos_lista(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    
    productos = Producto.objects.filter(activo=True)
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(marca__icontains=query)
        )
    
    if tipo:
        productos = productos.filter(tipo=tipo)
    
    context = {'productos': productos, 'query': query, 'tipo': tipo}
    return render(request, 'pos/productos.html', context)

@login_required
@rol_requerido('administrador', 'empleado')
def nueva_venta(request):
    if request.method == 'POST':
        # Procesar venta
        cliente_id = request.POST.get('cliente_id')
        metodo_pago = request.POST.get('metodo_pago')
        productos_ids = request.POST.getlist('producto_id[]')
        cantidades = request.POST.getlist('cantidad[]')
        
        # Crear venta
        folio = f"V-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        venta = Venta.objects.create(
            folio=folio,
            cliente_id=cliente_id if cliente_id else None,
            usuario=request.user,
            metodo_pago=metodo_pago
        )
        
        subtotal = 0
        for prod_id, cant in zip(productos_ids, cantidades):
            producto = Producto.objects.get(id=prod_id)
            cantidad = int(cant)
            precio = producto.precio_venta
            
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=cantidad * precio
            )
            subtotal += cantidad * precio
        
        venta.subtotal = subtotal
        venta.total = subtotal
        venta.save()
        
        messages.success(request, f'Venta {folio} registrada exitosamente')
        return redirect('historial_ventas')
    
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    clientes = Cliente.objects.all()
    context = {'productos': productos, 'clientes': clientes}
    return render(request, 'pos/nueva_venta.html', context)

@login_required
def historial_ventas(request):
    ventas = Venta.objects.all()

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)

    monto_total = ventas.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'pos/historial_ventas.html', {
        'ventas': ventas,
        'monto_total': monto_total
    })

@login_required
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)

    total = 0
    for d in detalles:
        d.subtotal = d.cantidad * d.precio_unitario
        total += d.subtotal

    return render(request, 'pos/detalle_venta.html', {
        'venta': venta,
        'detalles': detalles,
        'total': total,
    })

@login_required
def ticket_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)

    # Tamaño de ticket: 80mm x longitud variable
    alto = 180 + (len(detalles) * 10)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ticket_venta_{venta.id}.pdf"'

    p = canvas.Canvas(response, pagesize=(80*mm, alto*mm))
    y = alto*mm - 10

    tienda = "Zapatería - POS"
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(40*mm, y, tienda)
    y -= 5*mm

    p.setFont("Helvetica", 8)
    p.drawString(5*mm, y, f"Folio: {venta.folio}")
    y -= 4*mm
    p.drawString(5*mm, y, f"Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}")
    y -= 4*mm
    cliente = venta.cliente.nombre if venta.cliente else "Público General"
    p.drawString(5*mm, y, f"Cliente: {cliente}")
    y -= 6*mm

    p.line(0, y, 80*mm, y)
    y -= 5*mm

    p.setFont("Helvetica-Bold", 8)
    p.drawString(5*mm, y, "Producto")
    p.drawString(50*mm, y, "Sub")
    y -= 4*mm
    p.line(0, y, 80*mm, y)
    y -= 4*mm

    p.setFont("Helvetica", 8)

    for item in detalles:
        nombre_producto = item.producto.nombre
        subtotal = item.cantidad * item.precio_unitario

        p.drawString(5*mm, y, f"{item.cantidad}x {nombre_producto[:15]}")
        p.drawRightString(75*mm, y, f"${subtotal:.2f}")
        y -= 4*mm

    y -= 3*mm
    p.line(0, y, 80*mm, y)
    y -= 6*mm

    p.setFont("Helvetica-Bold", 9)
    p.drawString(5*mm, y, "TOTAL:")
    p.drawRightString(75*mm, y, f"${venta.total:.2f}")
    y -= 12*mm

    p.setFont("Helvetica", 7)
    p.drawCentredString(40*mm, y, "¡Gracias por su compra! 😄")

    p.showPage()
    p.save()
    return response


@login_required
def clientes_lista(request):
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    context = {'clientes': clientes}
    return render(request, 'pos/clientes.html', context)

@login_required
def proveedores_lista(request):
    proveedores = Proveedor.objects.filter(activo=True)
    context = {'proveedores': proveedores}
    return render(request, 'pos/proveedores.html', context)

@login_required
@rol_requerido('administrador', 'empleado')
def nueva_compra(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor_id')
        productos_ids = request.POST.getlist('producto_id[]')
        cantidades = request.POST.getlist('cantidad[]')
        precios = request.POST.getlist('precio[]')
        
        folio = f"C-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        compra = Compra.objects.create(
            folio=folio,
            proveedor_id=proveedor_id,
            usuario=request.user
        )
        
        total = 0
        for prod_id, cant, precio in zip(productos_ids, cantidades, precios):
            cantidad = int(cant)
            precio_unit = float(precio)
            
            DetalleCompra.objects.create(
                compra=compra,
                producto_id=prod_id,
                cantidad=cantidad,
                precio_unitario=precio_unit,
                subtotal=cantidad * precio_unit
            )
            total += cantidad * precio_unit
        
        compra.total = total
        compra.save()
        
        messages.success(request, f'Compra {folio} registrada exitosamente')
        return redirect('historial_compras')
    
    productos = Producto.objects.filter(activo=True)
    proveedores = Proveedor.objects.filter(activo=True)
    context = {'productos': productos, 'proveedores': proveedores}
    return render(request, 'pos/nueva_compra.html', context)

@login_required
def detalle_compra(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    detalles = DetalleCompra.objects.filter(compra=compra)

    # Cálculo de subtotal por producto
    for item in detalles:
        item.subtotal = item.cantidad * item.precio_unitario

    total = compra.total if compra.total else sum(item.subtotal for item in detalles)

    return render(request, 'pos/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles,
        'total': total
    })

@login_required
def historial_compras(request):
    compras = Compra.objects.all()
    context = {'compras': compras}
    return render(request, 'pos/historial_compras.html', context)

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Compra, DetalleCompra

@login_required
def compra_pdf(request, compra_id):
    compra = Compra.objects.get(id=compra_id)
    detalles = DetalleCompra.objects.filter(compra=compra)

    # Respuesta en PDF
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="compra_{compra.folio}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"Detalle de Compra - Folio {compra.folio}")
    y -= 30

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Fecha: {compra.fecha.strftime('%d/%m/%Y %H:%M')}")
    y -= 15
    p.drawString(50, y, f"Proveedor: {compra.proveedor.nombre}")
    y -= 15
    p.drawString(50, y, f"Usuario: {compra.usuario.username}")
    y -= 25

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Producto")
    p.drawString(250, y, "Cantidad")
    p.drawString(330, y, "Precio")
    p.drawString(400, y, "Subtotal")
    y -= 15

    p.setFont("Helvetica", 10)

    for item in detalles:
        if y < 50:  # Nueva página si no cabe
            p.showPage()
            y = height - 50
        
        p.drawString(50, y, item.producto.nombre[:25])
        p.drawString(250, y, str(item.cantidad))
        p.drawString(330, y, f"${item.precio_unitario:.2f}")
        p.drawString(400, y, f"${item.subtotal:.2f}")
        y -= 15

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total: ${compra.total:.2f}")

    p.showPage()
    p.save()
    return response


# ==========================================
# VISTAS PARA FORMULARIOS DE GESTIÓN
# ==========================================

from .forms import ProductoForm, ClienteForm, ProveedorForm, UsuarioForm

# PRODUCTOS
@login_required
@rol_requerido('administrador')
def producto_nuevo(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('productos')
    else:
        form = ProductoForm()
    return render(request, 'pos/producto_form.html', {'form': form, 'titulo': 'Nuevo Producto'})

@login_required
@rol_requerido('administrador', 'empleado')
def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'pos/producto_detalle.html', {'producto': producto})

@login_required
@rol_requerido('administrador')
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'pos/producto_form.html', {'form': form, 'titulo': 'Editar Producto', 'producto': producto})

@login_required
@rol_requerido('administrador')
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.activo = False
        producto.save()
        messages.success(request, 'Producto desactivado exitosamente')
        return redirect('productos')
    return render(request, 'pos/producto_confirmar_eliminar.html', {'producto': producto})

# CLIENTES
@login_required
@rol_requerido('administrador', 'empleado')
def cliente_nuevo(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente')
            return redirect('clientes')
    else:
        form = ClienteForm()
    return render(request, 'pos/cliente_form.html', {'form': form, 'titulo': 'Nuevo Cliente'})

@login_required
@rol_requerido('administrador', 'empleado')
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'pos/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente', 'cliente': cliente})

@login_required
@require_POST
def cliente_eliminar(request, cliente_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        cliente.delete()
        return JsonResponse({"status": "ok"})
    except Cliente.DoesNotExist:
        return JsonResponse({"status": "error"}, status=404)    
# PROVEEDORES
@login_required
@rol_requerido('administrador')
def proveedor_nuevo(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente')
            return redirect('proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'pos/proveedor_form.html', {'form': form, 'titulo': 'Nuevo Proveedor'})

@login_required
@rol_requerido('administrador')
def proveedor_editar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente')
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'pos/proveedor_form.html', {'form': form, 'titulo': 'Editar Proveedor', 'proveedor': proveedor})

# USUARIOS
@login_required
@rol_requerido('administrador')
def usuarios_lista(request):
    usuarios = Usuario.objects.all().order_by('-date_joined')
    context = {'usuarios': usuarios}
    return render(request, 'pos/usuarios.html', context)

@login_required
@rol_requerido('administrador')
def usuario_nuevo(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente')
            return redirect('usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'pos/usuario_form.html', {'form': form, 'titulo': 'Nuevo Usuario'})

@login_required
@rol_requerido('administrador')
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'pos/usuario_form.html', {'form': form, 'titulo': 'Editar Usuario', 'usuario': usuario})