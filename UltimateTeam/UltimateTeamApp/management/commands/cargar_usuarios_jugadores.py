from django.core.management.base import BaseCommand
from faker import Faker
from ...models import *
import random
from django.db import transaction

class Command(BaseCommand):
    help = 'Añade 30 usuarios y 150 cartas de jugadores (de forma acumulativa)'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la inserción de nuevos datos...'))

        fake = Faker('es_ES')

        self.stdout.write('Comprobando/Creando Ligas y Países...')

        ligas_nombres = ['LaLiga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1', 'MLS']
        ligas_en_db = []
        for nombre in ligas_nombres:
            liga_obj, created = Liga.objects.get_or_create(nombre=nombre)
            ligas_en_db.append(liga_obj)

        paises_nombres = set()
        while len(paises_nombres) < 50:
            paises_nombres.add(fake.country())

        paises_en_db = []
        for nombre in paises_nombres:
            pais_obj, created = Pais.objects.get_or_create(nombre=nombre)
            paises_en_db.append(pais_obj)

        self.stdout.write(self.style.SUCCESS(f'--- Ligas y Países listos ---'))

        usuarios_creados = 0
        for _ in range(30):
            try:
                usuario_obj, created = Usuario.objects.get_or_create(
                    email=fake.unique.email(),
                    defaults={'nombre': fake.name()}
                )
                if created:
                    usuarios_creados += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'No se pudo crear usuario (posible duplicado): {e}'))

        self.stdout.write(self.style.SUCCESS(f'--- {usuarios_creados} nuevos Usuarios creados ---'))

        cartas_creadas = 0
        posiciones_validas = [pos[0] for pos in CartasJugadore.Posiciones.choices]

        for _ in range(150):
            posicion_elegida = random.choice(posiciones_validas)

            stats_campo = {}
            stats_portero = {}

            if posicion_elegida == 'POR':
                stats_portero = {
                    'estirada': random.randint(50, 99), 'parada': random.randint(50, 99),
                    'saque': random.randint(50, 99), 'reflejos': random.randint(50, 99),
                    'posicionamiento': random.randint(50, 99), 'velocidad': random.randint(50, 99),
                }
                stats_campo = {
                    'ritmo': None, 'tiro': None, 'pase': None,
                    'regate': None, 'defensa': None, 'fisico': None
                }
            else:
                stats_campo = {
                    'ritmo': random.randint(50, 99), 'tiro': random.randint(40, 99),
                    'pase': random.randint(40, 99), 'regate': random.randint(40, 99),
                    'defensa': random.randint(30, 99), 'fisico': random.randint(40, 99),
                }
                stats_portero = {
                    'estirada': None, 'parada': None, 'saque': None,
                    'reflejos': None, 'posicionamiento': None, 'velocidad': None
                }

            try:
                CartasJugadore.objects.create(
                    nombre=fake.name(),
                    pais=random.choice(paises_en_db),
                    posicion=posicion_elegida,
                    liga=random.choice(ligas_en_db),
                    esta_activa=True,
                    **stats_campo,
                    **stats_portero
                )
                cartas_creadas += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'No se pudo crear carta: {e}'))

        self.stdout.write(self.style.SUCCESS(f'--- {cartas_creadas} nuevas Cartas creadas ---'))
        self.stdout.write(self.style.SUCCESS('¡Proceso de carga masiva completado!'))