from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.telefono})"


class Equipo(models.Model):
    tipo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=100)
    imei = models.CharField(max_length=30, unique=True, blank=True, null=True)
    serie = models.CharField(max_length=30, unique=True, blank=True, null=True)
    fecha_compra = models.DateField(blank=True, null=True)
    garantia_compra = models.BooleanField(default=False)
    accesorios = models.TextField(blank=True, null=True)
    estado_general = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} {self.marca} {self.modelo}"


class Orden(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=100, default='Pendiente')
    falla = models.CharField(max_length=250, blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    reparacion = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    fecha_entrega = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente.nombre}"
