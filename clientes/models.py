from django.db import models

class Cliente(models.Model):
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=120, blank=True)
    puntos = models.IntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.dni} - {self.nombre} ({self.puntos} pts)"
