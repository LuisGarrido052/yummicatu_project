"""
Formularios de la aplicación Repostería - Negocio Yummi Catu.
- RegistroCompradorForm: alta de cuentas de compradores (extiende UserCreationForm).
- ClienteDatosForm: edición de "Mis datos" del comprador.
- SolicitudGestionForm y ProductoForm: panel del vendedor.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction

from .models import Cliente, Producto, Solicitud
from .validators import validar_run

GRUPO_COMPRADORES = 'Compradores'
GRUPO_VENDEDORES = 'Vendedores'


class RegistroCompradorForm(UserCreationForm):
    run = forms.CharField(
        label='RUN', max_length=12,
        help_text='Sin puntos y con guion verificador. Ej: 12345678-9',
        widget=forms.TextInput(attrs={'placeholder': '12345678-9', 'autocomplete': 'off'}),
    )
    nombre = forms.CharField(label='Nombre', max_length=100)
    apellido = forms.CharField(label='Apellido', max_length=100)
    correo = forms.EmailField(label='Correo electrónico')
    telefono = forms.CharField(
        label='Teléfono / WhatsApp', max_length=12,
        widget=forms.TextInput(attrs={'placeholder': '+56912345678', 'type': 'tel'}),
    )

    class Meta(UserCreationForm.Meta):
        fields = ('username',)

    field_order = ['run', 'nombre', 'apellido', 'correo', 'telefono', 'username', 'password1', 'password2']

    def clean_run(self):
        run = validar_run(self.cleaned_data['run'])
        cliente = Cliente.objects.filter(run_cliente=run).first()
        if cliente and cliente.usuario_id:
            raise forms.ValidationError(
                'Este RUN ya tiene una cuenta. Ingresa con tu usuario o recupera tu contraseña.'
            )
        return run

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['correo']
        user.first_name = self.cleaned_data['nombre']
        user.last_name = self.cleaned_data['apellido']
        user.save()

        # Si el cliente ya había hecho encargos sin cuenta, se vincula su ficha existente
        Cliente.objects.update_or_create(
            run_cliente=self.cleaned_data['run'],
            defaults={
                'nombre_cliente': self.cleaned_data['nombre'],
                'apellido': self.cleaned_data['apellido'],
                'correo': self.cleaned_data['correo'],
                'telefono': self.cleaned_data['telefono'],
                'usuario': user,
            },
        )
        grupo, _ = Group.objects.get_or_create(name=GRUPO_COMPRADORES)
        user.groups.add(grupo)
        return user


class ClienteDatosForm(forms.ModelForm):
    """Mis datos: el RUN es la clave primaria y no se puede cambiar"""

    class Meta:
        model = Cliente
        fields = ['nombre_cliente', 'apellido', 'correo', 'telefono']


class SolicitudGestionForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['estado', 'fecha_entrega']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'descripcion', 'precio', 'destacado', 'imagen_subida']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
