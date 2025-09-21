from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Orden
from .forms import OrdenForm

class OrdenCreateView(CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'ordenes/orden_form.html'   # Ruta relativa dentro de templates/
    success_url = reverse_lazy('orden_nueva')   # Vuelve al mismo form al crear la orden


from django.shortcuts import render, redirect
from .forms import OrdenForm

def crear_orden(request):
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crear_orden')
    else:
        form = OrdenForm()
    return render(request, 'ordenes/crear_orden.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import ClienteForm, EquipoForm, OrdenForm

def crear_orden_integrada(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        equipo_form = EquipoForm(request.POST)
        orden_form = OrdenForm(request.POST)
        if cliente_form.is_valid() and equipo_form.is_valid() and orden_form.is_valid():
            cliente_data = cliente_form.cleaned_data
            cliente, creado = Cliente.objects.get_or_create(
                nombre=cliente_data['nombre'],
                telefono=cliente_data['telefono'],
                defaults=cliente_data
            )
            imei = equipo_form.cleaned_data.get('imei')
            equipo = Equipo.objects.filter(imei=imei).first()
            
            if not equipo:
                equipo = equipo_form.save()
            
            orden = orden_form.save(commit=False)
            orden.cliente = cliente
            orden.equipo = equipo
            orden.save()
            return redirect('crear_orden_integrada')
    else:
        cliente_form = ClienteForm()
        equipo_form = EquipoForm()
        orden_form = OrdenForm()
    return render(request, 'ordenes/crear_orden_integrada.html', {
        'cliente_form': cliente_form,
        'equipo_form': equipo_form,
        'orden_form': orden_form
    })

from django.http import JsonResponse
from .models import Cliente, Equipo, Orden

def buscar_clientes(request):
    query = request.GET.get('q', '')
    resultados = Cliente.objects.filter(nombre__icontains=query)[:10]
    data = []
    for cliente in resultados:
        # Buscar equipos relacionados a través de órdenes
        equipos = Equipo.objects.filter(orden__cliente=cliente).distinct()
        equipos_data = [
            f"{e.tipo} {e.marca} {e.modelo} (IMEI: {e.imei or 'N/A'} Serie: {e.serie or 'N/A'})"
            for e in equipos
        ]
        data.append({
            'id': cliente.id,
            'nombre': cliente.nombre,
            'telefono': cliente.telefono,
            'email': cliente.email,
            'direccion': cliente.direccion,
            'localidad': cliente.localidad,
            'provincia': cliente.provincia,
            'comentarios': cliente.comentarios,
            'equipos': equipos_data,
        })
    return JsonResponse({'clientes': data})


from django.http import JsonResponse
from .models import Equipo

def buscar_equipo_por_imei(request):
    imei = request.GET.get('imei', '')
    try:
        equipo = Equipo.objects.get(imei=imei)
        data = {
            'equipo': {
                'tipo': equipo.tipo,
                'marca': equipo.marca,
                'modelo': equipo.modelo,
                'serie': equipo.serie,
            }
        }
    except Equipo.DoesNotExist:
        data = {'equipo': None}
    return JsonResponse(data)

from django.shortcuts import render

def panel_principal(request):
    return render(request, 'ordenes/panel_principal.html')


from django.shortcuts import render
from .models import Equipo

def vista_equipos(request):
    equipos = Equipo.objects.all()
    return render(request, 'ordenes/vista_equipos.html', {'equipos': equipos})


from .models import Cliente

def vista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'ordenes/vista_clientes.html', {'clientes': clientes})


from django.shortcuts import render
from .models import Orden

def vista_historial(request):
    estado = request.GET.get('estado')  # ← Captura el estado desde la URL
    if estado:
        ordenes = Orden.objects.filter(estado=estado)
    else:
        ordenes = Orden.objects.all().order_by('-fecha_ingreso')[:50]

    return render(request, 'ordenes/vista_historial.html', {
        'ordenes': ordenes,
        'estado_seleccionado': estado  # ← Para que el template recuerde la opción elegida
    })
