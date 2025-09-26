from django.urls import path
from .views import (
    OrdenCreateView,
    crear_orden,
    crear_orden_integrada,
    buscar_clientes,
    buscar_equipo_por_imei,
    panel_principal,
    vista_equipos,
    vista_clientes,
    vista_historial,
    vista_equipos_parcial,
    vista_clientes_parcial,
    vista_ordenes_parcial,
    vista_historial_parcial,  # ← corregido si existe
    detalle_orden_modal,
    nuevo_cliente_modal,
    editar_cliente_modal,
    eliminar_cliente,
    
)


urlpatterns = [
    # Panel principal
    path('', panel_principal, name='panel_principal'),
    path('panel/', panel_principal, name='panel_principal'),

    # Crear orden
    path('crear/', crear_orden, name='crear_orden'),
    path('crear-integrada/', crear_orden_integrada, name='crear_orden_integrada'),
    path('orden/nueva/', OrdenCreateView.as_view(), name='orden_nueva'),

    # Buscar cliente y equipo
    path('buscar-clientes/', buscar_clientes, name='buscar_clientes'),
    path('buscar-equipo/', buscar_equipo_por_imei, name='buscar_equipo_por_imei'),

    # Vistas principales
    path('vista-equipos/', vista_equipos, name='vista_equipos'),
    path('vista-clientes/', vista_clientes, name='vista_clientes'),
    path('vista-historial/', vista_historial, name='vista_historial'),

    # Vistas parciales
    path('equipos/parcial/', vista_equipos_parcial, name='vista_equipos_parcial'),
    path('clientes/parcial/', vista_clientes_parcial, name='vista_clientes_parcial'),
    path('ordenes/parcial/', vista_ordenes_parcial, name='vista_ordenes_parcial'),
    path('historial/parcial/', vista_historial_parcial, name='vista_historial_parcial'),

    # Modales
    path('detalle/<int:orden_id>/', detalle_orden_modal, name='detalle_orden_modal'),
    path('clientes/nuevo/', nuevo_cliente_modal, name='nuevo_cliente_modal'),
    path('clientes/editar/<int:cliente_id>/', editar_cliente_modal, name='editar_cliente_modal'),
    path('clientes/eliminar/<int:cliente_id>/', eliminar_cliente, name='eliminar_cliente'),

    #Historial parcial
    path('historial/parcial/', vista_historial_parcial, name='vista_historial_parcial'),



]
