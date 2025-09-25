# ordenes/views.py (bloque completo y limpio)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.generic.edit import CreateView
from django.views.decorators.csrf import csrf_exempt

from .models import Cliente, Equipo, Orden
from .forms import ClienteForm, EquipoForm, OrdenForm


class OrdenCreateView(CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'ordenes/orden_form.html'
    success_url = reverse_lazy('orden_nueva')  # ajusta si tu nombre de url es distinto


def crear_orden(request):
    """Vista simple usando solo OrdenForm (si la usás en alguna parte)."""
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crear_orden')
    else:
        form = OrdenForm()
    return render(request, 'ordenes/crear_orden.html', {'form': form})


def crear_orden_integrada(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST, prefix='cliente')
        equipo_form  = EquipoForm(request.POST, prefix='equipo')
        orden_form   = OrdenForm(request.POST, prefix='orden')

        # Primero validamos cliente; si cliente inválido mostramos errores sin crear equipo/orden
        if not cliente_form.is_valid():
            return render(request, 'ordenes/crear_orden_integrada.html', {
                'cliente_form': cliente_form, 'equipo_form': equipo_form, 'orden_form': orden_form
            })

        # Si el cliente está ok, validamos equipo y orden
        if not (equipo_form.is_valid() and orden_form.is_valid()):
            return render(request, 'ordenes/crear_orden_integrada.html', {
                'cliente_form': cliente_form, 'equipo_form': equipo_form, 'orden_form': orden_form
            })

        # Guardado atómico: cliente → equipo (si no existe por IMEI) → orden
        with transaction.atomic():
            cliente = cliente_form.save()
            imei = equipo_form.cleaned_data.get('imei')
            equipo = None
            if imei:
                equipo = Equipo.objects.filter(imei=imei).first()
            if not equipo:
                equipo = equipo_form.save()
            orden = orden_form.save(commit=False)
            orden.cliente = cliente
            orden.equipo = equipo
            orden.save()
        return redirect('vista_ordenes')  # ajusta nombre de vista
    else:
        cliente_form = ClienteForm(prefix='cliente')
        equipo_form  = EquipoForm(prefix='equipo')
        orden_form   = OrdenForm(prefix='orden')

    return render(request, 'ordenes/crear_orden_integrada.html', {
        'cliente_form': cliente_form, 'equipo_form': equipo_form, 'orden_form': orden_form
    })


def vista_ordenes_parcial(request):
    ordenes = Orden.objects.select_related('cliente', 'equipo').order_by('-fecha_ingreso')
    return render(request, 'ordenes/vista_ordenes_parcial.html', {
        'ordenes': ordenes
    })


def buscar_clientes(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.filter(
        nombre__icontains=q
    ) | Cliente.objects.filter(
        telefono__icontains=q
    )

    resultados = []
    for cliente in clientes.distinct():
        equipos = cliente.equipo_set.values_list('tipo', 'marca', 'modelo', 'imei', 'serie')
        equipos_texto = [
            f"{tipo} {marca} {modelo} (IMEI: {imei} Serie: {serie})"
            for tipo, marca, modelo, imei, serie in equipos
        ]
        resultados.append({
            'id': cliente.id,
            'nombre': cliente.nombre,
            'telefono': cliente.telefono,
            'email': cliente.email,
            'direccion': cliente.direccion,
            'localidad': cliente.localidad,
            'provincia': cliente.provincia,
            'comentarios': cliente.comentarios,
            'equipos': equipos_texto,
        })

    return JsonResponse({'clientes': resultados})


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


def panel_principal(request):
    return render(request, 'ordenes/panel_principal.html')


def vista_equipos(request):
    estado = request.GET.get('estado', '')
    cliente_q = request.GET.get('cliente', '')
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')

    ordenes = Orden.objects.select_related('equipo', 'cliente')

    if estado:
        ordenes = ordenes.filter(estado__icontains=estado)
    if cliente_q:
        ordenes = ordenes.filter(cliente__nombre__icontains=cliente_q)
    if marca:
        ordenes = ordenes.filter(equipo__marca__icontains=marca)
    if modelo:
        ordenes = ordenes.filter(equipo__modelo__icontains=modelo)

    ordenes = ordenes.order_by('-fecha_ingreso')

    return render(request, 'ordenes/vista_equipos.html', {
        'ordenes': ordenes,
        'estado': estado,
        'cliente': cliente_q,
        'marca': marca,
        'modelo': modelo,
    })


def vista_equipos_parcial(request):
    estado = request.GET.get('estado', '')
    cliente_q = request.GET.get('cliente', '')
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')

    ordenes = Orden.objects.select_related('equipo', 'cliente')

    if estado:
        ordenes = ordenes.filter(estado__icontains=estado)
    if cliente_q:
        ordenes = ordenes.filter(cliente__nombre__icontains=cliente_q)
    if marca:
        ordenes = ordenes.filter(equipo__marca__icontains=marca)
    if modelo:
        ordenes = ordenes.filter(equipo__modelo__icontains=modelo)

    ordenes = ordenes.order_by('-fecha_ingreso')

    return render(request, 'ordenes/vista_equipos_parcial.html', {
        'ordenes': ordenes,
        'estado': estado,
        'cliente': cliente_q,
        'marca': marca,
        'modelo': modelo,
    })


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


def vista_clientes_parcial(request):
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'ordenes/vista_clientes_parcial.html', {
        'clientes': clientes
    })


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


def vista_historial(request):
    estado = request.GET.get('estado')
    if estado:
        ordenes = Orden.objects.filter(estado=estado)
    else:
        ordenes = Orden.objects.all().order_by('-fecha_ingreso')[:50]

    return render(request, 'ordenes/vista_historial.html', {
        'ordenes': ordenes,
        'estado_seleccionado': estado
    })


def vista_historial_parcial(request):
    historial = Orden.objects.select_related('cliente', 'equipo').order_by('-fecha_ingreso')
    return render(request, 'ordenes/vista_historial_parcial.html', {
        'historial': historial
    })


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


@csrf_exempt
def eliminar_cliente(request, cliente_id):
    if request.method == 'POST':
        Cliente.objects.filter(id=cliente_id).delete()
        return HttpResponse("Eliminado")
    return HttpResponse("Método no permitido", status=405)




def vista_historial_parcial(request):
    ordenes = Orden.objects.select_related('cliente', 'equipo').order_by('-fecha_ingreso')
    return render(request, 'ordenes/vista_historial_parcial.html', {'ordenes': ordenes})
