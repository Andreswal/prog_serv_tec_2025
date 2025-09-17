from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    comentarios = models.CharField(max_length=250, blank=True, null=True)
    def __str__(self):
        return f"{self.nombre} ({self.telefono})"

class Equipo(models.Model):
    imei = models.CharField(max_length=30, blank=True, null=True, unique=True)
    serie = models.CharField(max_length=30, blank=True, null=True, unique=True) 
    tipo = models.CharField(max_length=50)     # Ej: celular, tablet, notebook
    marca = models.CharField(max_length=50)    # Ej: Samsung, Apple
    modelo = models.CharField(max_length=50)   # Ej: A32, iPhone 11
    fecha_compra = models.DateField(blank=True, null=True)
    garantia_compra = models.BooleanField(default=False)
    accesorios = models.CharField(max_length=100, blank=True, null=True)
    estado_general = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.tipo} {self.marca} {self.modelo}"

class Orden(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=100, default='Pendiente')
    falla = models.CharField(max_length=250, blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    reparacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente.nombre} - {self.equipo.marca}"

# Create your models here.
