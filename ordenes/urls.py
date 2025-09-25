from django.urls import path
from .views import buscar_equipo_por_imei
from .views import (
    OrdenCreateView,
    crear_orden,
    crear_orden_integrada,
    buscar_clientes,
    panel_principal,
    vista_equipos,
    vista_clientes,
    vista_historial,
)
from .views import detalle_orden_modal
from .views import nuevo_cliente_modal
from .views import editar_cliente_modal
from .views import eliminar_cliente
from .views import vista_equipos_parcial
from .views import vista_clientes_parcial
from .views import vista_ordenes_parcial
from ordenes.views import panel_principal

urlpatterns = [
    path('orden/nueva/', OrdenCreateView.as_view(), name='orden_nueva'),
    path('crear/', crear_orden, name='crear_orden'),
    path('crear-integrada/', crear_orden_integrada, name='crear_orden_integrada'),
    path('buscar-clientes/', buscar_clientes, name='buscar_clientes'),
    path('buscar-equipo/', buscar_equipo_por_imei, name='buscar_equipo_por_imei'),
    path('', panel_principal, name='panel_principal'),
    path('vista-equipos/', vista_equipos, name='vista_equipos'),
    path('vista-clientes/', vista_clientes, name='vista_clientes'),
    path('vista-historial/', vista_historial, name='vista_historial'),
    path('detalle/<int:orden_id>/', detalle_orden_modal, name='detalle_orden_modal'),
    path('clientes/nuevo/', nuevo_cliente_modal, name='nuevo_cliente_modal'),
    path('clientes/editar/<int:cliente_id>/', editar_cliente_modal, name='editar_cliente_modal'),
    path('clientes/eliminar/<int:cliente_id>/', eliminar_cliente, name='eliminar_cliente'),
    path('equipos/parcial/', vista_equipos_parcial, name='vista_equipos_parcial'),
    path('clientes/parcial/', vista_clientes_parcial, name='vista_clientes_parcial'),
    path('ordenes/parcial/', vista_ordenes_parcial, name='vista_ordenes_parcial'),
    path('panel/', panel_principal, name='panel_principal'),


]



