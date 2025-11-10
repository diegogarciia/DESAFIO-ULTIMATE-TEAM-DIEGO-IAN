from django.test import TestCase, Client
from .models import Usuario, Equipo, CartasJugadore
import json

# Create your tests here.

class ModelosUnitTests(TestCase):

    def test_property_tipo_posicion(self):
        carta_defensa = CartasJugadore.objects.create(nombre="Ramos", posicion="DFC")
        carta_centro = CartasJugadore.objects.create(nombre="Modric", posicion="MC")
        carta_delantero = CartasJugadore.objects.create(nombre="Ronaldo", posicion="DC")
        carta_portero = CartasJugadore.objects.create(nombre="Casillas", posicion="POR")
        self.assertEqual(carta_defensa.tipo_posicion, 'Defensa')
        self.assertEqual(carta_centro.tipo_posicion, 'Centrocampista')
        self.assertEqual(carta_delantero.tipo_posicion, 'Delantero')
        self.assertEqual(carta_portero.tipo_posicion, 'Portero')

class VistasIntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nombre="Usuario de Prueba", email="test@test.com")
        self.equipo = Equipo.objects.create(nombre="Equipo de Prueba")
        self.usuario.equipo = self.equipo
        self.usuario.save()
        self.carta_activa = CartasJugadore.objects.create(
            nombre="Jugador Activo",
            posicion="DC",
            esta_activa=True
        )
        self.carta_inactiva = CartasJugadore.objects.create(
            nombre="Jugador Inactivo",
            posicion="MC",
            esta_activa=False
        )
        self.equipo.cartas.add(self.carta_activa, self.carta_inactiva)

    def test_get_equipo_usuario_req6(self):
        url = f'/api/usuarioConsultarEquipo/{self.usuario.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['propietario'], 'Usuario de Prueba')
        self.assertEqual(data['nombre_equipo'], 'Equipo de Prueba')
        self.assertEqual(len(data['cartas_activas']), 1)
        self.assertEqual(data['cartas_activas'][0]['nombre'], 'Jugador Activo')

    def test_get_equipo_usuario_sin_equipo(self):
        usuario_sin_equipo = Usuario.objects.create(nombre="Otro Usuario", email="test2@test.com")

        url = f'/api/usuarioConsultarEquipo/{usuario_sin_equipo.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Este usuario no tiene ningún equipo asignado.')

    def test_consultar_media_equipo(self):
        url = f'/api/usuarioConsultarMediaEquipo/{self.usuario.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

