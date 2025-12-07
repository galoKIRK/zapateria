# pos/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # Autenticación - Login en la raíz
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Productos
    path('productos/', views.productos_lista, name='productos'),
    path('productos/nuevo/', views.producto_nuevo, name='producto_nuevo'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('productos/<int:pk>/', views.producto_detalle, name='producto_detalle'),

    
    # Ventas
    path('venta/nueva/', views.nueva_venta, name='nueva_venta'),
    path('ventas/', views.historial_ventas, name='historial_ventas'),
    path('ventas/<int:venta_id>/detalle/', views.detalle_venta, name='detalle_venta'),
    path('ventas/<int:venta_id>/ticket/', views.ticket_pdf, name='ticket_pdf'),

    # Clientes
    path('clientes/', views.clientes_lista, name='clientes'),
    path('clientes/nuevo/', views.cliente_nuevo, name='cliente_nuevo'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path("clientes/eliminar/<int:cliente_id>/", views.cliente_eliminar, name="cliente_eliminar"),

    
    # Proveedores
    path('proveedores/', views.proveedores_lista, name='proveedores'),
    path('proveedores/nuevo/', views.proveedor_nuevo, name='proveedor_nuevo'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    
    # Compras
    path('compra/nueva/', views.nueva_compra, name='nueva_compra'),
    path('compras/', views.historial_compras, name='historial_compras'),
    path('compras/<int:compra_id>/detalle/', views.detalle_compra, name='detalle_compra'),
    path("compras/pdf/<int:compra_id>/", views.compra_pdf, name="compra_pdf"),
  
    
    # Usuarios
    path('usuarios/', views.usuarios_lista, name='usuarios'),
    path('usuarios/nuevo/', views.usuario_nuevo, name='usuario_nuevo'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)