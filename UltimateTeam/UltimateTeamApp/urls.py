from django.urls import path
from . import views

urlpatterns = [

    path('obtenerUsuario/<int:id>', views.get_usuario)

]