
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ordenes/', include('ordenes.urls')),  # ← aquí
    path('', include('ordenes.urls')),

]
