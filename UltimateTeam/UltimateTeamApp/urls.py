from django.urls import path
from . import views

urlpatterns = [

    #USUARIOS
    path('obtenerUsuario/<int:id>', views.get_usuarioID),
    path('obtenerUsuarios', views.get_usuarios),
    path('añadirUsuario', views.add_usuario),
    path('modificarUsuario/<int:id>', views.update_usuario),
    path('borrarUsuario/<int:id>', views.delete_usuario),
    path('asignarEquipo/<int:id>', views.asignar_equipo),

    #CARTA JUGADOR
    path('obtenerCartaJugador/<int:id>', views.get_cartaID),
    path('obtenerCartas',views.get_cartas),
    path('añadirCarta', views.add_carta),
    path('modificarCarta/<int:id>', views.update_carta),
    path('actualizarCarta/<int:id>', views.activar_carta),
    path('borrarCarta/<int:id>', views.desactivar_carta),

    #ASIGNAR EQUIPO A UN USUARIO
    path('usuario/asignarEquipo/<int:usuario_id>', views.asignar_equipo_servicio),

    #CONSULTAR EL EQUIPO DE UN USUARIO
    path('usuarioConsultarEquipo/<int:usuario_id>', views.get_equipo_usuario),

]