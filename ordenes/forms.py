
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from .models import Cliente, Equipo, Orden

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'cliente-form'
        self.helper.form_method = 'post'
        self.helper.form_tag = False  # ← evita que crispy genere <form>
        self.helper.layout = Layout(
            Fieldset('Datos del Cliente',
                'nombre', 'telefono', 'email',
                'direccion', 'localidad', 'provincia',
                'comentarios'
            )
        )

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'equipo-form'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset('Datos del Equipo',
                'tipo', 'marca', 'modelo',
                'imei', 'serie',
                'fecha_compra', 'garantia_compra',
                'accesorios', 'estado_general'
            )
        )

    def clean_imei(self):
        imei = self.cleaned_data.get('imei')
        if imei:
            qs = Equipo.objects.filter(imei=imei)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un equipo con este IMEI.")
        return imei

    def clean_serie(self):
        serie = self.cleaned_data.get('serie')
        if serie:
            qs = Equipo.objects.filter(serie=serie)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un equipo con este número de serie.")
        return serie

    
    

class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = '__all__'
        exclude = ['cliente', 'equipo']  # ← se asignan manualmente en la vista

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'orden-form'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset('Datos de la Orden',
                'estado', 'falla', 'diagnostico', 'reparacion',
                'observaciones', 'fecha_ingreso', 'fecha_entrega'
            )
        )

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'direccion', 'localidad', 'provincia', 'comentarios']