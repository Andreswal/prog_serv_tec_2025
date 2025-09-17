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
            cliente = cliente_form.save()
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
