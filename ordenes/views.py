# En ordenes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.generic.edit import CreateView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q # Importación necesaria
from django.views.decorators.http import require_POST
import json 

from .models import Cliente, Equipo, Orden # Asegúrate de que Cliente esté aquí
from .forms import ClienteForm, EquipoForm, OrdenForm

# ===============================================
# VISTAS DE ORDENES
# ===============================================

class OrdenCreateView(CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'ordenes/orden_form.html'
    success_url = reverse_lazy('orden_nueva') 

def crear_orden(request):
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

        if not (cliente_form.is_valid() and equipo_form.is_valid() and orden_form.is_valid()):
             return render(request, 'ordenes/crear_orden_integrada.html', {
                 'cliente_form': cliente_form, 'equipo_form': equipo_form, 'orden_form': orden_form
             })

        with transaction.atomic():
            cliente = cliente_form.save()
            imei = equipo_form.cleaned_data.get('imei')
            equipo = Equipo.objects.filter(imei=imei).first() if imei else None
            
            if not equipo:
                equipo = equipo_form.save() 
            
            orden = orden_form.save(commit=False)
            orden.cliente = cliente
            orden.equipo = equipo
            orden.save()
            
        return redirect('vista_ordenes') # Asume que tienes una URL llamada 'vista_ordenes'
    
    else:
        cliente_form = ClienteForm(prefix='cliente')
        equipo_form  = EquipoForm(prefix='equipo')
        orden_form   = OrdenForm(prefix='orden')

    return render(request, 'ordenes/crear_orden_integrada.html', {
        'cliente_form': cliente_form, 'equipo_form': equipo_form, 'orden_form': orden_form
    })
    
    
# En ordenes/views.py, añade esta nueva función
def crear_orden_integrada_precargada(request):
    """
    Vista de la orden integrada que precarga un cliente ID pasado por GET.
    """
    cliente = None
    cliente_id = request.GET.get('cliente_id')
    
    # 1. Lógica de Precarga (si viene de la lista de clientes)
    if cliente_id:
        try:
            cliente = Cliente.objects.get(pk=cliente_id)
        except Cliente.DoesNotExist:
            pass 

    # 2. Manejo POST (Guarda los 3 formularios)
    if request.method == 'POST':
        # Para el POST, si el cliente fue precargado, su instancia se usa para 
        # actualizarlo o asegurar que el form de cliente no falle si no tiene datos.
        instance_cliente = cliente if cliente else None
        
        # OJO: Si estás usando el mismo formulario, asegúrate que en el template
        # se maneje bien la instancia o la data inicial.
        cliente_form = ClienteForm(request.POST, prefix='cliente', instance=instance_cliente)
        equipo_form  = EquipoForm(request.POST, prefix='equipo')
        orden_form   = OrdenForm(request.POST, prefix='orden')

        # Si el cliente ya está cargado, no validamos el formulario de cliente
        is_cliente_valid = cliente_form.is_valid() if not cliente else True
        
        if not (is_cliente_valid and equipo_form.is_valid() and orden_form.is_valid()):
             # Si falla la validación, re-renderiza con los errores
             return render(request, 'ordenes/crear_orden_integrada.html', {
                 'cliente_form': cliente_form, 
                 'equipo_form': equipo_form, 
                 'orden_form': orden_form,
                 'cliente_seleccionado': cliente # Reenvía el cliente para el mensaje de precarga
             })

        with transaction.atomic():
            # Si el cliente es nuevo, lo guarda. Si ya existía, usamos la instancia cargada.
            if cliente: # Ya cargado desde GET
                pass # No se guarda/actualiza el ClienteForm si está precargado
            else: # No precargado, debe venir data en el ClienteForm
                cliente = cliente_form.save()
            
            imei = equipo_form.cleaned_data.get('imei')
            equipo = Equipo.objects.filter(imei=imei).first() if imei else None
            
            if not equipo:
                equipo = equipo_form.save() 
            
            orden = orden_form.save(commit=False)
            orden.cliente = cliente # Asigna el cliente (ya sea cargado o nuevo)
            orden.equipo = equipo
            orden.save()
            
        return redirect('vista_ordenes') 
    
    # 3. Manejo GET (Mostrar formularios)
    else:
        # Inicializa los formularios
        initial_cliente = {'id': cliente.id} if cliente else {} 
        
        # Cliente Form: Lo inicializamos con los datos del cliente si existe
        cliente_form = ClienteForm(prefix='cliente', initial=initial_cliente, instance=cliente)
        
        # Orden Form: Aquí precargamos el campo Cliente con el ID
        initial_orden = {'cliente': cliente.id} if cliente else {}
        orden_form  = OrdenForm(prefix='orden', initial=initial_orden)
        
        equipo_form  = EquipoForm(prefix='equipo')

    return render(request, 'ordenes/crear_orden_integrada.html', {
        'cliente_form': cliente_form, 
        'equipo_form': equipo_form, 
        'orden_form': orden_form,
        'cliente_seleccionado': cliente # Pasa el objeto cliente al template
    })


def vista_ordenes_parcial(request):
    ordenes = Orden.objects.select_related('cliente', 'equipo').order_by('-fecha_ingreso')
    return render(request, 'ordenes/vista_ordenes_parcial.html', {
        'ordenes': ordenes
    })
    
    
def crear_orden_view(request):
    """
    Vista para crear una nueva orden, permitiendo precargar el cliente ID desde GET.
    Si recibe POST, intenta guardar. Si falla, devuelve el formulario con errores.
    """
    cliente = None
    form = None
    
    # 1. Manejo de Cliente ID (Se ejecuta siempre al inicio, especialmente en GET)
    cliente_id = request.GET.get('cliente_id')
    if cliente_id:
        try:
            # Si el cliente existe, lo cargamos
            cliente = Cliente.objects.get(pk=cliente_id) 
        except Cliente.DoesNotExist:
            pass 

    # 2. Manejo de Petición POST (Guardado)
    if request.method == 'POST':
        form = OrdenForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            
            # Si el formulario no traía el cliente (ej. hidden field) y lo precargamos, 
            # aseguramos que se asigne a la orden
            if not orden.cliente and cliente:
                orden.cliente = cliente
                
            orden.save()
            
            # Respuesta JSON para AJAX si la operación fue exitosa
            return JsonResponse({'success': True, 'orden_id': orden.id}) 
            
        # Si NO es válido, el flujo continúa hacia el paso 3 para re-renderizar
        # el formulario con los errores.

    # 3. Manejo de Petición GET o POST Inválido (Mostrar/Re-mostrar formulario)
    
    # Si 'form' es None, significa que es una petición GET.
    if form is None:
        initial_data = {}
        if cliente:
            # Precarga el campo 'cliente' con el ID
            initial_data['cliente'] = cliente.id
            
        form = OrdenForm(initial=initial_data)

    # El render se ejecuta si es GET, o si es POST fallido.
    return render(request, 'ordenes/crear_orden.html', { 
        'form': form,
        'cliente_seleccionado': cliente 
    })
    
    
# ===============================================
# BUSQUEDA Y PANELES
# ===============================================

def buscar_clientes(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=q) | Q(telefono__icontains=q)
    ).distinct()

    resultados = []
    for cliente in clientes:
        # Nota: La relación de Equipo a Cliente debe llamarse 'equipo_set'
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

# ===============================================
# VISTAS AUXILIARES Y DE LISTADOS
# ===============================================

def _aplicar_filtros_ordenes(request, queryset=None):
    if queryset is None:
        queryset = Orden.objects.select_related('equipo', 'cliente')
        
    estado = request.GET.get('estado', '')
    cliente_q = request.GET.get('cliente', '')
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')
    
    if estado: queryset = queryset.filter(estado__icontains=estado)
    if cliente_q: queryset = queryset.filter(cliente__nombre__icontains=cliente_q)
    if marca: queryset = queryset.filter(equipo__marca__icontains=marca)
    if modelo: queryset = queryset.filter(equipo__modelo__icontains=modelo)
        
    return queryset.order_by('-fecha_ingreso'), {
        'estado': estado, 'cliente': cliente_q, 'marca': marca, 'modelo': modelo,
    }

def vista_equipos(request):
    ordenes, filtros = _aplicar_filtros_ordenes(request)
    return render(request, 'ordenes/vista_equipos.html', {'ordenes': ordenes, **filtros})


def vista_equipos_parcial(request):
    ordenes, filtros = _aplicar_filtros_ordenes(request)
    return render(request, 'ordenes/vista_equipos_parcial.html', {'ordenes': ordenes, **filtros})

def vista_clientes(request):
    nombre = request.GET.get('nombre', '')
    telefono = request.GET.get('telefono', '')
    email = request.GET.get('email', '')
    ordenar_por = request.GET.get('ordenar_por', 'nombre')
    direccion = request.GET.get('direccion', 'asc')

    clientes = Cliente.objects.all()

    if nombre: clientes = clientes.filter(nombre__icontains=nombre)
    if telefono: clientes = clientes.filter(telefono__icontains=telefono)
    if email: clientes = clientes.filter(email__icontains=email)

    if direccion == 'desc': ordenar_por = f'-{ordenar_por}'
    clientes = clientes.order_by(ordenar_por)

    return render(request, 'ordenes/vista_clientes.html', {
        'clientes': clientes,
        'nombre': nombre, 'telefono': telefono, 'email': email,
        'ordenar_por': request.GET.get('ordenar_por', ''), 'direccion': direccion,
    })


def vista_clientes_parcial(request):
    q = request.GET.get('q', '')
    
    if q:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=q) | Q(telefono__icontains=q)
        ).distinct()
        clientes = clientes.order_by('nombre')
    else:
        clientes = Cliente.objects.all()
        clientes = clientes.order_by('nombre')
        
    return render(request, 'ordenes/vista_clientes_parcial.html', {'clientes': clientes, 'q': q})


def vista_historial(request):
    """Vista principal de historial. Reinsertada para solucionar el ImportError en urls.py."""
    estado = request.GET.get('estado')
    ordenes = Orden.objects.select_related('cliente', 'equipo') 
    
    if estado:
        ordenes = ordenes.filter(estado=estado)
        
    ordenes = ordenes.order_by('-fecha_ingreso')[:50] # Límite para evitar cargas muy pesadas
    
    return render(request, 'ordenes/vista_historial.html', {
        'ordenes': ordenes,
        'estado_seleccionado': estado
    })


def vista_historial_parcial(request):
    # Puedes usar _aplicar_filtros_ordenes aquí si lo deseas. 
    # Por ahora, solo devuelve un contexto vacío si no hay lógica de filtrado compleja.
    context = {
        'historial_items': Orden.objects.select_related('cliente', 'equipo').order_by('-fecha_ingreso')[:20]
    }
    return render(request, 'ordenes/vista_historial_parcial.html', context)


def detalle_orden_modal(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    cliente = orden.cliente
    equipo = orden.equipo

    if request.method == 'POST':
        form = OrdenForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            return HttpResponse("Guardado")
        # Aquí faltaría manejar el error de validación
    else:
        form = OrdenForm(instance=orden)

    return render(request, 'ordenes/modal_orden.html', {
        'form': form,
        'orden': orden,
        'cliente': cliente,
        'equipo': equipo,
    })

# ===============================================
# VISTAS AJAX DE CLIENTES
# ===============================================

def guardar_cliente_ajax(request):
    """Vista para CREAR un nuevo cliente."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            try:
                cliente = form.save()
                
                if is_ajax:
                    # Se incluye 'success': True para consistencia con el frontend
                    return JsonResponse({
                        'success': True,  
                        'id': cliente.id,
                        'nombre': cliente.nombre,
                        'telefono': cliente.telefono,
                        'email': cliente.email or '',
                        'direccion': cliente.direccion or '',
                        'localidad': cliente.localidad or '',
                        'provincia': cliente.provincia or '',
                        'comentarios': cliente.comentarios or ''
                    })
                else:
                    return redirect('vista_clientes')
                    
            except Exception as e:
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': [str(e)]}}, status=500)
                else:
                    return render(request, 'ordenes/crear_cliente.html', {'form': form, 'error': str(e)})
        else:
            # Formulario inválido
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            else:
                return render(request, 'ordenes/crear_cliente.html', {'form': form})
    
    else:
        # GET: Mostrar formulario
        form = ClienteForm()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        template = 'ordenes/form_cliente_parcial.html' if is_ajax else 'ordenes/crear_cliente.html'
        
        return render(request, template, {'form': form, 'cliente_id': None}) 

    
def editar_cliente_ajax(request, cliente_id):
    """Vista para EDITAR un cliente existente."""
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'action': 'updated'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    else:
        form = ClienteForm(instance=cliente)
        return render(request, 'ordenes/form_cliente_parcial.html', {
            'form': form,
            'cliente_id': cliente_id 
        })
        
@require_POST
def eliminar_clientes_ajax(request):
    """Vista para eliminar clientes de forma masiva (AJAX)."""
    cliente_ids = request.POST.getlist('cliente_ids[]') 
    
    if not cliente_ids:
        return JsonResponse({'success': False, 'message': 'No se proporcionaron IDs.'}, status=400)

    delete_count = Cliente.objects.filter(id__in=cliente_ids).delete()
    
    return JsonResponse({
        'success': True,
        'count': delete_count[0], 
    })


@csrf_exempt
def eliminar_cliente(request, cliente_id):
    """Eliminar un único cliente (URL separada)."""
    if request.method == 'POST':
        Cliente.objects.filter(id=cliente_id).delete()
        return HttpResponse("Eliminado")
    return HttpResponse("Método no permitido", status=405)