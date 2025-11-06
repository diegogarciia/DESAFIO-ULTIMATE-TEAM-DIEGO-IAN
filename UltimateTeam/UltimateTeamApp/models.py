from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.

from django.db import models
from django.core.exceptions import ValidationError

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        if hasattr(self, 'usuario'):
            return f"{self.nombre}"
        return self.nombre

class Usuario(models.Model):

    nombre = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    equipo = models.OneToOneField(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuario'
    )

    def __str__(self):
        return self.nombre

class CartasJugadore(models.Model):
    class Posiciones(models.TextChoices):
        POR = 'POR'
        DFC = 'DFC'
        LI = 'LI'
        LD = 'LD'
        MCD = 'MCD'
        MC = 'MC'
        MI = 'MI'
        MD = 'MD'
        MCO = 'MCO'
        DC = 'DC'
        SD = 'SD'
        EI = 'EI'
        ED = 'ED'

    nombre = models.CharField(max_length=100)
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cartas'
    )
    pais = models.CharField(max_length=50)
    posicion = models.CharField(
        max_length=3,
        choices=Posiciones.choices,
    )
    liga = models.CharField(max_length=100)

    ritmo = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    tiro = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    pase = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    regate = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    defensa = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    fisico = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])

    estirada = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    parada = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    saque = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    reflejos = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    posicionamiento = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])
    velocidad = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(99), MinValueValidator(1)])

    esta_activa = models.BooleanField(default=True)

    media = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Se calcula automáticamente al guardar. Los atributos como máximo pueden ser 99"
    )

    def __str__(self):
        return f"{self.nombre} ({self.posicion}) ({self.media})"

    def clean(self):
        super().clean()

        if self.posicion == 'POR':
            if (self.ritmo is not None or self.tiro is not None or
                    self.pase is not None or self.regate is not None or
                    self.defensa is not None or self.fisico is not None):
                raise ValidationError(
                    'Un Portero (POR) no puede tener estadísticas de jugador de campo (ritmo, tiro, etc.). Déjalas en blanco.'
                )

        else:
            if (self.estirada is not None or self.parada is not None or
                    self.saque is not None or self.reflejos is not None or
                    self.posicionamiento is not None or self.velocidad is not None):
                raise ValidationError(
                    f'Un jugador con posición {self.posicion} no puede tener estadísticas de portero. Déjalas en blanco.'
                )

    @property
    def valoracion_general(self):

        if self.posicion == self.Posiciones.POR:
            stats_portero = [
                (self.estirada or 0),
                (self.parada or 0),
                (self.saque or 0),
                (self.reflejos or 0),
                (self.posicionamiento or 0),
                (self.velocidad or 0)
            ]
            if not stats_portero: return 0
            media = sum(stats_portero) / len(stats_portero)
            return int(round(media))

        stats_campo = {
            'ritmo': (self.ritmo or 0),
            'tiro': (self.tiro or 0),
            'pase': (self.pase or 0),
            'regate': (self.regate or 0),
            'defensa': (self.defensa or 0),
            'fisico': (self.fisico or 0)
        }

        if self.posicion in [self.Posiciones.DFC, self.Posiciones.LI,
                             self.Posiciones.LD]:
            pesos = {'defensa': 0.30, 'fisico': 0.25, 'pase': 0.15, 'ritmo': 0.10, 'regate': 0.10, 'tiro': 0.10}

        elif self.posicion in [self.Posiciones.MC, self.Posiciones.MI,
                               self.Posiciones.MD, self.Posiciones.MCO,
                               self.Posiciones.MCD]:
            pesos = {'pase': 0.30, 'regate': 0.25, 'tiro': 0.15, 'defensa': 0.10, 'ritmo': 0.10, 'fisico': 0.10}

        else:
            pesos = {'tiro': 0.30, 'regate': 0.25, 'ritmo': 0.20, 'fisico': 0.10, 'pase': 0.10, 'defensa': 0.05}

        valoracion_total = 0
        for stat, valor in stats_campo.items():
            valoracion_total += valor * pesos[stat]

        return int(round(valoracion_total))

    def save(self, *args, **kwargs):
        self.clean()
        self.media = self.valoracion_general
        super().save(*args, **kwargs)

    @property
    def tipo_posicion(self):

        if self.posicion == self.Posiciones.POR:
            return 'Portero'

        if self.posicion in [self.Posiciones.DFC, self.Posiciones.LI, self.Posiciones.LD]:
            return 'Defensa'

        if self.posicion in [self.Posiciones.MCD, self.Posiciones.MC, self.Posiciones.MI,
                             self.Posiciones.MD, self.Posiciones.MCO]:
            return 'Centrocampista'

        if self.posicion in [self.Posiciones.DC, self.Posiciones.SD, self.Posiciones.EI, self.Posiciones.ED]:
            return 'Delantero'
