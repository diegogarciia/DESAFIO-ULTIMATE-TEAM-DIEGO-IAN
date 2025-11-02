from django.db import models

# Create your models here.

from django.db import models

class Usuario(models.Model):

    nombre = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre