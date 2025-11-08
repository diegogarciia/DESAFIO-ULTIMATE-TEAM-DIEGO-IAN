# DESAFÍO FIFA Ultimate Team

Este proyecto es el back-end para el "DESAFÍO FIFA Ultimate Team" de la asignatura de Programación de Aplicaciones Utilizando Frameworks. Es una API REST desarrollada en Django que gestiona un sistema de cartas, usuarios y equipos inspirado en el modo "Ultimate Team".

El proyecto se centra en la lógica del servidor, la definición de modelos, las relaciones de la base de datos (incluyendo OneToOne y ManyToManyField) y la creación de endpoints para operaciones CRUD y servicios de lógica de negocio complejos.

✒️ Autores

Diego García

Ian Gabriel Castellanos

🚀 Tecnologías Utilizadas

Python 3.11+

Django 5.0+

Faker: Para la generación de datos masivos.

SQLite3: Como motor de base de datos de desarrollo.

✨ Funcionalidades Implementadas

Req 1: CRUD completo para el modelo Usuario.

Req 2: CRUD completo para CartasJugadore, implementando borrado lógico (esta_activa) y validando que una carta en un equipo no pueda ser modificada o borrada.

Req 3 y 3.1: Un servicio especial (/api/usuario/asignarEquipo/<int:id>) que crea un Equipo nuevo para un usuario y lo rellena automáticamente con 23-25 jugadores, respetando las cuotas de posición (porteros, defensas, etc.).

Req 4: Cálculo automático de la valoración media (media) de la carta, usando una media ponderada basada en la posición del jugador. Se ejecuta automáticamente al guardar (.save()).

Req 5: Un comando de gestión personalizado (cargar_usuarios_jugadores) que usa Faker para poblar la base de datos con Ligas, Países, 30 Usuarios y 150 Cartas "libres".

Req 6: Un endpoint (/api/usuarioConsultarEquipo/<int:id>) para consultar el equipo completo de un usuario, mostrando solo sus cartas activas y los nombres de país/liga.

Req 7: Un endpoint (/api/add_carta_to_equipo/<int:id>) para añadir una carta específica a un equipo, validando los límites totales (25) y por posición (ej: máx. 3 porteros).

Normalización: Creación de modelos Pais y Liga (ForeignKey) para normalizar la base de datos y evitar la redundancia de datos.

Modelo de Datos Avanzado: Implementación de relaciones OneToOne (Usuario <-> Equipo) y ManyToManyField (Equipo <-> CartasJugadore) para permitir que un jugador esté en múltiples equipos.

Validación de Modelos: Uso del método clean() en CartasJugadore para asegurar que los porteros no tengan estadísticas de jugador y viceversa.

Pruebas (RA5): Implementación de pruebas unitarias (para models.py) y pruebas de integración (para views.py) usando TestCase de Django.

🏁 Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en un entorno local.

1. Clonar el repositorio

git clone https://github.com/diegogarciia/DESAFIO-ULTIMATE-TEAM-DIEGO-IAN.git

2. Crear y activar un entorno virtual

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
