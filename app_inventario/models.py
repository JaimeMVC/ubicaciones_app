from django.db import models


class LocationCheck(models.Model):
    pn = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    checked_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('pn', 'ubicacion')
        ordering = ['pn', 'ubicacion']


class LocationBase(models.Model):
    pn = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('pn', 'ubicacion')
        ordering = ['pn', 'ubicacion']


class CountSession(models.Model):
    pn = models.CharField(max_length=50)
    operador = models.CharField(max_length=100)
    comentario = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']


class CountDetail(models.Model):
    session = models.ForeignKey(CountSession, on_delete=models.CASCADE, related_name='detalles')
    base = models.ForeignKey(LocationBase, on_delete=models.CASCADE, related_name='conteos')
    revisado = models.BooleanField(default=False)
    fecha_revision = models.DateTimeField(blank=True, null=True)
    # 👉 NUEVO: cantidad de piezas encontradas en esa ubicación
    cantidad = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('session', 'base')


class ResultSnapshot(models.Model):
    pn = models.CharField(max_length=50)
    total = models.IntegerField()
    revisadas = models.IntegerField()
    porcentaje = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pn} | {self.porcentaje}% | {self.created_at.strftime('%Y-%m-%d %H:%M')}"
