from django.http import JsonResponse

# Create your views here.

from .models import Usuario
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def get_usuario(request, id):
    if request.method == "GET":
        try:
            usuario = Usuario.objects.values().get(id=id)
            return JsonResponse(usuario)
        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
    else:
        return JsonResponse({"error": "Operación no soportada"})