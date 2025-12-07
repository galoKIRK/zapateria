from django import forms
from .models import Producto, Cliente, Proveedor, Usuario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'tipo', 'marca', 'talla', 'color', 
                  'descripcion', 'precio_compra', 'precio_venta', 'stock', 
                  'stock_minimo', 'imagen', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: NK-001-42'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Nike, Adidas'}),
            'talla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 42, 38'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Negro, Blanco'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del producto'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'codigo': 'Código *',
            'nombre': 'Nombre *',
            'tipo': 'Tipo *',
            'marca': 'Marca *',
            'talla': 'Talla *',
            'color': 'Color *',
            'descripcion': 'Descripción',
            'precio_compra': 'Precio de Compra *',
            'precio_venta': 'Precio de Venta *',
            'stock': 'Stock Inicial *',
            'stock_minimo': 'Stock Mínimo *',
            'imagen': 'Imagen',
            'activo': 'Producto Activo',
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del cliente'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5512345678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'cliente@ejemplo.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
        }
        labels = {
            'nombre': 'Nombre Completo *',
            'telefono': 'Teléfono *',
            'email': 'Correo Electrónico',
            'direccion': 'Dirección',
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'rfc', 'telefono', 'email', 'direccion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa'}),
            'rfc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RFC a 13 caracteres'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5512345678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@proveedor.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre de la Empresa *',
            'rfc': 'RFC *',
            'telefono': 'Teléfono *',
            'email': 'Correo Electrónico *',
            'direccion': 'Dirección *',
            'activo': 'Proveedor Activo',
        }

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña *',
        required=False,
        help_text='Dejar en blanco para no cambiar la contraseña'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Contraseña *',
        required=False
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'rol', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5512345678'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Nombre de Usuario *',
            'first_name': 'Nombre *',
            'last_name': 'Apellidos *',
            'email': 'Correo Electrónico *',
            'telefono': 'Teléfono',
            'rol': 'Rol *',
            'is_active': 'Usuario Activo',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user