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
from .models import Orden

def vista_equipos(request):
    estado = request.GET.get('estado', '')
    cliente = request.GET.get('cliente', '')
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')

    ordenes = Orden.objects.select_related('equipo', 'cliente')

    if estado:
        ordenes = ordenes.filter(estado__icontains=estado)
    if cliente:
        ordenes = ordenes.filter(cliente__nombre__icontains=cliente)
    if marca:
        ordenes = ordenes.filter(equipo__marca__icontains=marca)
    if modelo:
        ordenes = ordenes.filter(equipo__modelo__icontains=modelo)

    ordenes = ordenes.order_by('-fecha_ingreso')

    return render(request, 'ordenes/vista_equipos.html', {
        'ordenes': ordenes,
        'estado': estado,
        'cliente': cliente,
        'marca': marca,
        'modelo': modelo,
    })
    

from django.shortcuts import render
from .models import Cliente

def vista_clientes(request):
    nombre = request.GET.get('nombre', '')
    telefono = request.GET.get('telefono', '')
    email = request.GET.get('email', '')
    ordenar_por = request.GET.get('ordenar_por', 'nombre')
    direccion = request.GET.get('direccion', 'asc')

    clientes = Cliente.objects.all()

    if nombre:
        clientes = clientes.filter(nombre__icontains=nombre)
    if telefono:
        clientes = clientes.filter(telefono__icontains=telefono)
    if email:
        clientes = clientes.filter(email__icontains=email)

    if direccion == 'desc':
        ordenar_por = f'-{ordenar_por}'

    clientes = clientes.order_by(ordenar_por)

    return render(request, 'ordenes/vista_clientes.html', {
        'clientes': clientes,
        'nombre': nombre,
        'telefono': telefono,
        'email': email,
        'ordenar_por': request.GET.get('ordenar_por', ''),
        'direccion': direccion,
    })



from django.shortcuts import render
from django.http import JsonResponse
from .forms import ClienteForm

def nuevo_cliente_modal(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'telefono': cliente.telefono,
                'email': cliente.email,
                'direccion': cliente.direccion,
                'localidad': cliente.localidad,
                'provincia': cliente.provincia,
                'comentarios': cliente.comentarios,
            })
    else:
        form = ClienteForm()
    return render(request, 'ordenes/modal_cliente.html', {'form': form})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Cliente
from .forms import ClienteForm

def editar_cliente_modal(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'telefono': cliente.telefono,
                'email': cliente.email,
                'direccion': cliente.direccion,
                'localidad': cliente.localidad,
                'provincia': cliente.provincia,
                'comentarios': cliente.comentarios,
            })
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'ordenes/modal_editar_cliente.html', {'form': form, 'cliente': cliente})



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


from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Orden
from .forms import OrdenForm

def detalle_orden_modal(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    cliente = orden.cliente
    equipo = orden.equipo

    if request.method == 'POST':
        form = OrdenForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            return HttpResponse("Guardado")
    else:
        form = OrdenForm(instance=orden)

    return render(request, 'ordenes/modal_orden.html', {
        'form': form,
        'orden': orden,
        'cliente': cliente,
        'equipo': equipo,
    })

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Cliente

@csrf_exempt
def eliminar_cliente(request, cliente_id):
    if request.method == 'POST':
        Cliente.objects.filter(id=cliente_id).delete()
        return HttpResponse("Eliminado")
    return HttpResponse("Método no permitido", status=405)



