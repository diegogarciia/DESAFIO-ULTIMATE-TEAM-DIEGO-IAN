from django.core.management.base import BaseCommand
from faker import Faker
from ...models import *
import random

class Command(BaseCommand):
    help = 'Crea 30 usuarios y 150 cartas de jugadores'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la creación de datos...'))

        fake = Faker('es_ES')

        usuarios_creados = 0
        for _ in range(30):
            try:
                Usuario.objects.create(
                    nombre=fake.unique.name(),
                    email=fake.unique.email()
                    # No asignamos equipo, cumpliendo Req5
                )
                usuarios_creados += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'No se pudo crear usuario (posible duplicado): {e}'))

        self.stdout.write(self.style.SUCCESS(f'--- {usuarios_creados} Usuarios creados ---'))

        cartas_creadas = 0

        posiciones_validas = [pos[0] for pos in CartasJugadore.Posiciones.choices]

        for _ in range(150):
            posicion_elegida = random.choice(posiciones_validas)

            stats_campo = {}
            stats_portero = {}

            if posicion_elegida == 'POR':
                stats_portero = {
                    'estirada': random.randint(50, 99),
                    'parada': random.randint(50, 99),
                    'saque': random.randint(50, 99),
                    'reflejos': random.randint(50, 99),
                    'posicionamiento': random.randint(50, 99),
                    'velocidad': random.randint(50, 99),
                }
                stats_campo = {
                    'ritmo': None, 'tiro': None, 'pase': None,
                    'regate': None, 'defensa': None, 'fisico': None
                }
            else:
                stats_campo = {
                    'ritmo': random.randint(50, 99),
                    'tiro': random.randint(40, 99),
                    'pase': random.randint(40, 99),
                    'regate': random.randint(40, 99),
                    'defensa': random.randint(30, 99),
                    'fisico': random.randint(40, 99),
                }
                stats_portero = {
                    'estirada': None, 'parada': None, 'saque': None,
                    'reflejos': None, 'posicionamiento': None, 'velocidad': None
                }

            try:
                CartasJugadore.objects.create(
                    nombre=fake.name(),
                    pais=fake.country(),
                    posicion=posicion_elegida,
                    liga=random.choice(['LaLiga', 'Premier League', 'Serie A', 'Bundesliga']),
                    esta_activa=True,
                    # No asignamos equipo, cumpliendo Req5

                    **stats_campo,
                    **stats_portero
                )
                cartas_creadas += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'No se pudo crear carta: {e}'))

        self.stdout.write(self.style.SUCCESS(f'--- {cartas_creadas} Cartas creadas ---'))
        self.stdout.write(self.style.SUCCESS('¡Proceso de carga masiva completado!'))