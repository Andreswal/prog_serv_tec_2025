from django.urls import path
from . import views # ⬅️ Solo importamos el módulo 'views' completo
# ❌ Eliminamos la importación explícita de funciones que causaba el error:
# from .views import ( ... ) 

urlpatterns = [
    # Panel principal
    path('', views.panel_principal, name='panel_principal'),
    path('panel/', views.panel_principal, name='panel_principal'),

    # Crear orden
    path('crear/', views.crear_orden, name='crear_orden'),
    path('crear-integrada/', views.crear_orden_integrada, name='crear_orden_integrada'),
    path('orden/nueva/', views.OrdenCreateView.as_view(), name='orden_nueva'),

    # Buscar cliente y equipo
    path('buscar-clientes/', views.buscar_clientes, name='buscar_clientes'),
    path('buscar-equipo/', views.buscar_equipo_por_imei, name='buscar_equipo_por_imei'),

    # Vistas principales
    path('vista-equipos/', views.vista_equipos, name='vista_equipos'),
    path('vista-clientes/', views.vista_clientes, name='vista_clientes'),
    # 💥 Usamos views.vista_historial
    path('vista-historial/', views.vista_historial, name='vista_historial'), 

    # Vistas parciales
    path('equipos/parcial/', views.vista_equipos_parcial, name='vista_equipos_parcial'),
    path('clientes/parcial/', views.vista_clientes_parcial, name='vista_clientes_parcial'),
    path('ordenes/parcial/', views.vista_ordenes_parcial, name='vista_ordenes_parcial'),
    path('historial/parcial/', views.vista_historial_parcial, name='vista_historial_parcial'),

    # Modales - Órdenes
    path('detalle/<int:orden_id>/', views.detalle_orden_modal, name='detalle_orden_modal'),

    # ========================================
    # CLIENTES - URLs consolidadas y sin duplicados
    # ========================================
    
    # Crear nuevo cliente (GET: formulario, POST: guardar)
    path('clientes/nuevo/', views.guardar_cliente_ajax, name='guardar_cliente'),
    
    # Editar cliente existente
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente_ajax, name='editar_cliente'),
    
    # Eliminar varios clientes (AJAX)
    path('clientes/eliminar/', views.eliminar_clientes_ajax, name='eliminar_clientes_ajax'),
    
    # Eliminar un cliente específico
    path('clientes/eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
]