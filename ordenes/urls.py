from django.urls import path
from .views import OrdenCreateView
from .views import crear_orden
from .views import crear_orden_integrada

urlpatterns = [
    path('orden/nueva/', OrdenCreateView.as_view(), name='orden_nueva'),
    path('crear/', crear_orden, name='crear_orden'),
    path('crear-integrada/', crear_orden_integrada, name='crear_orden_integrada'),
    
]

from .views import buscar_clientes

urlpatterns = [
    path('crear-integrada/', crear_orden_integrada, name='crear_orden_integrada'),
    path('buscar-clientes/', buscar_clientes, name='buscar_clientes'),
]
