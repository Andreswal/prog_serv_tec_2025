from django.urls import path
from .views import buscar_equipo_por_imei
from .views import (
    OrdenCreateView,
    crear_orden,
    crear_orden_integrada,
    buscar_clientes
)


urlpatterns = [
    path('orden/nueva/', OrdenCreateView.as_view(), name='orden_nueva'),
    path('crear/', crear_orden, name='crear_orden'),
    path('crear-integrada/', crear_orden_integrada, name='crear_orden_integrada'),
    path('buscar-clientes/', buscar_clientes, name='buscar_clientes'),
    path('buscar-equipo/', buscar_equipo_por_imei, name='buscar_equipo_por_imei'),
    
]



