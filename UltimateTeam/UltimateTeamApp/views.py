import json
from django.http import JsonResponse

# Create your views here.

from .models import Usuario, Equipo
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def get_usuarioID(request, id):
    if request.method == "GET":
        try:
            usuario = Usuario.objects.values().get(id=id)
            return JsonResponse(usuario)
        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
    else:
        return JsonResponse({"error": "Operación no soportada"})



def get_usuarios(request):
    usuarios = Usuario.objects.all().values()
    return JsonResponse(list(usuarios),safe=False)



@csrf_exempt
def add_usuario(request):
    if request.method  == 'POST':
        jsonUsuario = json.loads(request.body)
        usuario = Usuario.objects.create(**jsonUsuario)
        return JsonResponse({"usuario": "Se ha insertado correctamente"})
    else:
        return JsonResponse({"error": "Operación no soportada"})




@csrf_exempt
def update_usuario(request, id):
    if request.method in ('PUT', 'PATCH'):
        try:
            usuario = Usuario.objects.get(id=id)

            data = json.loads(request.body)

            for key, value in data.items():
                setattr(usuario, key, value)

            usuario.save()
            return JsonResponse({"mensaje": f"Usuario con ID {id} actualizado correctamente"})

        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)

        except Exception as e:
            return JsonResponse({"error": f"Error al actualizar el usuario: {str(e)}"}, status=400)

    else:
        return JsonResponse({"error": "Método no soportado. Usa PUT o PATCH."}, status=405)



@csrf_exempt
def asignar_equipo(request, id):

    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=id)
        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado."}, status=404)


        if usuario.equipo is not None:

            return JsonResponse({
                "error": "El usuario ya tiene un equipo asociado.",
                "equipo_actual": usuario.equipo.nombre,
                "mensaje": "Debe eliminar la asociación del equipo previamente para poder asignar uno nuevo."
            }, status=400)

        try:

            data = json.loads(request.body)
            id_equipo = data.get('id_equipo')

            if id_equipo is None:
                return JsonResponse({"error": "Se requiere el 'id_equipo' en el cuerpo de la solicitud."}, status=400)


            equipo = Equipo.objects.get(id=id_equipo)


            usuario.equipo = equipo
            usuario.save()


            return JsonResponse({
                "mensaje": f"El equipo '{equipo.nombre}' ha sido asignado correctamente al usuario '{usuario.nombre}'."
            })

        except Equipo.DoesNotExist:
            return JsonResponse({"error": f"Equipo con ID {id_equipo} no encontrado."}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al asignar el equipo: {str(e)}"}, status=500)

    else:

        return JsonResponse({"error": "Método no soportado. Usa POST."}, status=405)


@csrf_exempt
def delete_usuario(request, id):
    if request.method == 'DELETE':
        try:
            usuario = Usuario.objects.get(pk=id)
            usuario.delete()
            return JsonResponse({'mensaje': 'Usuario eliminado correctamente'})
        except Usuario.DoesNotExist as e:
            return JsonResponse({"error": "Error al borrar el usuario" + e.message}, status=404)
