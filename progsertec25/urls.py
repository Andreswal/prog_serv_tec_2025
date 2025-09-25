from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ordenes/', include('ordenes.urls')),
    path('', include('ordenes.urls')),  # ← esta línea conecta la raíz "/"
]

