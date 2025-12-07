# pos/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('empleado', 'Empleado'),
        ('consulta', 'Consulta'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='empleado')
    telefono = models.CharField(max_length=15, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    rfc = models.CharField(max_length=13, unique=True)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    direccion = models.TextField()
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = 'Proveedores'

class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    TIPOS = (
        ('casual', 'Casual'),
        ('deportivo', 'Deportivo'),
    )
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    marca = models.CharField(max_length=100)
    talla = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.marca} - Talla {self.talla}"
    
    @property
    def necesita_reposicion(self):
        return self.stock <= self.stock_minimo

class Compra(models.Model):
    folio = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    
    def __str__(self):
        return f"Compra {self.folio} - {self.proveedor.nombre}"
    
    class Meta:
        ordering = ['-fecha']

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Venta(models.Model):
    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    )
    
    folio = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    notas = models.TextField(blank=True)
    
    def __str__(self):
        return f"Venta {self.folio} - ${self.total}"
    
    class Meta:
        ordering = ['-fecha']

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

# SIGNALS PARA ACTUALIZAR STOCK
@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_venta(sender, instance, created, **kwargs):
    if created:
        # Restar del stock cuando se crea una venta
        Producto.objects.filter(pk=instance.producto.pk).update(
            stock=models.F('stock') - instance.cantidad
        )

@receiver(post_save, sender=DetalleCompra)
def actualizar_stock_compra(sender, instance, created, **kwargs):
    if created:
        # Sumar al stock cuando se crea una compra
        Producto.objects.filter(pk=instance.producto.pk).update(
            stock=models.F('stock') + instance.cantidad
        )