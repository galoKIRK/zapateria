from django.contrib import admin
from .models import Usuario, Producto, Cliente, Proveedor, Venta, DetalleVenta, Compra, DetalleCompra

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'rol', 'is_active']
    list_filter = ['rol', 'is_active']
    search_fields = ['username', 'email']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'marca', 'talla', 'precio_venta', 'stock']
    list_filter = ['tipo', 'marca', 'activo']
    search_fields = ['codigo', 'nombre', 'marca']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'fecha_registro']
    search_fields = ['nombre', 'telefono']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rfc', 'telefono', 'activo']
    search_fields = ['nombre', 'rfc']

admin.site.register(Venta)
admin.site.register(Compra)