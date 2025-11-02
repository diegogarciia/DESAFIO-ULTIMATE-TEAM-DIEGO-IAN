from django.http import JsonResponse

# Create your views here.

from rest_framework import viewsets, status
from .models import Usuario

class UsuarioViewSet(viewsets.ModelViewSet):

    def get_usuario(request, id):
        if request.method == "GET":
            try:
                usuario = Usuario.objects.values().get(id=id)
                return JsonResponse(usuario)
            except Usuario.DoesNotExist:
                return JsonResponse({"error": "Usuario no encontrado"}, status=404)
        else:
            return JsonResponse({"error": "Operación no soportada"})