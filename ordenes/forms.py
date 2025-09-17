
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from .models import Cliente, Equipo, Orden

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'direccion', 'localidad', 'provincia', 'comentarios']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'cliente-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Datos del Cliente',
                'nombre', 'telefono', 'email',
                'direccion', 'localidad', 'provincia',
                'comentarios'
            ),
            ButtonHolder(
                Submit('submit', 'Guardar Cliente', css_class='btn-primary')
            )
        )

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['imei', 'serie', 'tipo', 'marca', 'modelo',
                  'fecha_compra', 'garantia_compra',
                  'accesorios', 'estado_general']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'equipo-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Detalles del Equipo',
                'imei', 'serie',
                'tipo', 'marca', 'modelo',
                'fecha_compra', 'garantia_compra',
                'accesorios', 'estado_general'
            ),
            ButtonHolder(
                Submit('submit', 'Guardar Equipo', css_class='btn-primary')
            )
        )

class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['estado', 'falla', 'diagnostico', 'reparacion']  # cliente y equipo se asignan en la vista

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'orden-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Nueva Orden',
                'estado', 'falla',
                'diagnostico', 'reparacion'
            ),
            ButtonHolder(
                Submit('submit', 'Crear Orden', css_class='btn-success')
            )
        )

