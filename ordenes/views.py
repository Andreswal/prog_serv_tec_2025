# ordenes/views.py (bloque revisado)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.generic.edit import CreateView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q # Importación necesaria (ya estaba, pero la mantengo aquí)

from .models import Cliente, Equipo, Orden
from .forms import ClienteForm, EquipoForm, OrdenForm


class OrdenCreateView(CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'ordenes/orden_form.html'
    success_url = reverse_lazy('orden_nueva') 


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

        # Si alguna validación falla, renderiza el formulario con los errores
        if not (cliente_form.is_valid() and equipo_form.is_valid() and orden_form.is_valid()):
             return render(request, 'ordenes/crear_orden_integrada.html', {
                'cliente_form': cliente_form, 'equipo_form': equipo_form, 'orden_form': orden_form
            })

        # Guardado atómico: cliente → equipo (si no existe por IMEI) → orden
        with transaction.atomic():
            # 1. Guardar o actualizar cliente
            cliente = cliente_form.save() # Si tiene un ID, se actualiza; si no, se crea.
            
            # 2. Manejar Equipo (crear o reutilizar por IMEI)
            imei = equipo_form.cleaned_data.get('imei')
            equipo = None
            if imei:
                equipo = Equipo.objects.filter(imei=imei).first()
            
            # Si no encontramos equipo por IMEI, o si IMEI está vacío, creamos uno nuevo.
            if not equipo:
                equipo = equipo_form.save() 
            
            # 3. Guardar Orden
            orden = orden_form.save(commit=False)
            orden.cliente = cliente
            orden.equipo = equipo
            orden.save()
            
        return redirect('vista_ordenes') # Ajusta nombre de vista si es necesario
    
    else:
        cliente_form = ClienteForm(prefix='cliente')
        equipo_form  = EquipoForm(prefix='equipo')
        orden_form   = OrdenForm(prefix='orden')

    return render(request, 'ordenes/crear_orden_integrada.html', {
        'cliente_form': cliente_form, 'equipo_form': equipo_form, 'orden_form': orden_form
    })


def vista_ordenes_parcial(request):
    # Sin filtros, solo lista
    ordenes = Orden.objects.select_related('cliente', 'equipo').order_by('-fecha_ingreso')
    return render(request, 'ordenes/vista_ordenes_parcial.html', {
        'ordenes': ordenes
    })


def buscar_clientes(request):
    q = request.GET.get('q', '')
    
    # 1. Usar Q objects y el operador | (OR) de forma limpia
    # NOTA: Tu lógica ya estaba correcta, solo la refactorizo para ser más concisa.
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=q) | Q(telefono__icontains=q)
    ).distinct()

    resultados = []
    for cliente in clientes:
        # Optimización: solo trae los campos necesarios
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


def _aplicar_filtros_ordenes(request, queryset=None):
    """Función auxiliar para aplicar filtros comunes a las OTs. (Refactorización)"""
    if queryset is None:
        queryset = Orden.objects.select_related('equipo', 'cliente')
        
    estado = request.GET.get('estado', '')
    cliente_q = request.GET.get('cliente', '')
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')
    
    if estado:
        queryset = queryset.filter(estado__icontains=estado)
    if cliente_q:
        queryset = queryset.filter(cliente__nombre__icontains=cliente_q)
    if marca:
        queryset = queryset.filter(equipo__marca__icontains=marca)
    if modelo:
        queryset = queryset.filter(equipo__modelo__icontains=modelo)
        
    return queryset.order_by('-fecha_ingreso'), {
        'estado': estado,
        'cliente': cliente_q,
        'marca': marca,
        'modelo': modelo,
    }

# Vistas de equipos y parcial refactorizadas para usar la función auxiliar
def vista_equipos(request):
    ordenes, filtros = _aplicar_filtros_ordenes(request)
    return render(request, 'ordenes/vista_equipos.html', {'ordenes': ordenes, **filtros})


def vista_equipos_parcial(request):
    ordenes, filtros = _aplicar_filtros_ordenes(request)
    return render(request, 'ordenes/vista_equipos_parcial.html', {'ordenes': ordenes, **filtros})
# Fin de la refactorización


def vista_clientes(request):
    nombre = request.GET.get('nombre', '')
    telefono = request.GET.get('telefono', '')
    email = request.GET.get('email', '')
    ordenar_por = request.GET.get('ordenar_por', 'nombre')
    direccion = request.GET.get('direccion', 'asc')

    clientes = Cliente.objects.all()

    # Filtros de cliente (ya estaban correctos)
    if nombre:
        clientes = clientes.filter(nombre__icontains=nombre)
    if telefono:
        clientes = clientes.filter(telefono__icontains=telefono)
    if email:
        clientes = clientes.filter(email__icontains=email)

    # Lógica de ordenamiento
    if direccion == 'desc':
        ordenar_por = f'-{ordenar_por}'

    clientes = clientes.order_by(ordenar_por)

    return render(request, 'ordenes/vista_clientes.html', {
        'clientes': clientes,
        # Se envían los valores de filtro de vuelta al template para mostrarlos en los inputs
        'nombre': nombre,
        'telefono': telefono,
        'email': email,
        'ordenar_por': request.GET.get('ordenar_por', ''),
        'direccion': direccion,
    })


def vista_clientes_parcial(request):
    q = request.GET.get('q', '')
    # Lógica de filtrado con Q-objects para el campo de búsqueda rápida 'q'
    # Esta es la lógica que debe estar en concordancia con tu formulario HTML
    if q:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=q) | Q(telefono__icontains=q)
        ).distinct()
    else:
        clientes = Cliente.objects.all()
        
    return render(request, 'ordenes/vista_clientes_parcial.html', {'clientes': clientes, 'q': q})



def nuevo_cliente_modal(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            # Retorno de datos JSON (ya estaba correcto)
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
            # Retorno de datos JSON (ya estaba correcto)
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
    # La vista original usaba .filter(estado=estado), sin icontains, lo cual está bien si el estado es exacto
    estado = request.GET.get('estado')
    ordenes = Orden.objects.select_related('cliente', 'equipo') # Añadido select_related para optimizar
    
    if estado:
        ordenes = ordenes.filter(estado=estado)
    else:
        # Aquí puedes decidir si quieres listar todo o limitar (como ya tenías)
        ordenes = ordenes.all()
        
    ordenes = ordenes.order_by('-fecha_ingreso')[:50] # Límite para evitar cargas muy pesadas
    
    return render(request, 'ordenes/vista_historial.html', {
        'ordenes': ordenes,
        'estado_seleccionado': estado
    })


# Eliminada la segunda definición de vista_historial_parcial
# El contenido se integra en la función general de historial si se usa para filtrar


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


# En ordenes/views.py
# ... tus otras funciones ...

def vista_historial_parcial(request):
    # Aquí iría tu lógica para obtener el historial filtrado
    context = {
        'historial_items': [] # O Cliente.objects.none() por defecto
    }
    # Asegúrate de tener una plantilla llamada 'vista_historial_parcial.html'
    return render(request, 'ordenes/vista_historial_parcial.html', context)



def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            # 👉 Después de guardar, devolvemos la plantilla con el marcador
            return render(request, 'ordenes/cliente_creado_cerrar.html', {'cliente': cliente})
    else:
        form = ClienteForm()

    # 👉 Si es GET o el formulario no es válido, mostramos el formulario normal
    return render(request, 'ordenes/crear_cliente.html', {'form': form})


