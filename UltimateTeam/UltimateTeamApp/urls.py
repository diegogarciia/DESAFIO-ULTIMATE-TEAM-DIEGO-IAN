from django.urls import path
from . import views

urlpatterns = [
    path('obtenerUsuario/<int:id>', views.get_usuarioID),
    path('obtenerUsuarios', views.get_usuarios),
    path('añadirUsuario', views.add_usuario),
    path('modificarUsuario/<int:id>', views.update_usuario),
    path('borrarUsuario/<int:id>', views.delete_usuario),
    path('asignarEquipo/<int:id>', views.asignar_equipo)
]