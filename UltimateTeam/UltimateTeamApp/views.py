import json
import random

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import JsonResponse

# Create your views here.

from .models import Usuario, Equipo, CartasJugadore
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

ATRIBUTOS_JUGADOR = ["ritmo", "tiro", "pase", "regate", "defensa", "fisico"]
ATRIBUTOS_PORTERO = ["estirada", "parada", "saque", "reflejos", "posicionamiento", "velocidad"]
LIMITES_EQUIPO = {
    'total': {'min': 23, 'max': 25},
    'Portero': {'min': 2, 'max': 3},
    'Defensa': {'min': 8, 'max': 10},
    'Centrocampista': {'min': 6, 'max': 9},
    'Delantero': {'min': 5, 'max': 6},
}

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




def get_cartaID(request, id):
    if request.method == "GET":
        try:
            carta = CartasJugadore.objects.get(id=id)

            if carta.equipos.count() > 0:
                return JsonResponse({
                    "error": f"La carta con ID {id} pertenece a {carta.equipos.count()} equipo(s) y no puede ser consultada individualmente."
                }, status=403)

            carta_jugador = CartasJugadore.objects.values().get(id=id)

            if carta_jugador.get('posicion') == 'POR':
                for key in ATRIBUTOS_JUGADOR:
                    if key in carta_jugador:
                        del carta_jugador[key]

            if carta_jugador.get('posicion') != 'POR':
                for key in ATRIBUTOS_PORTERO:
                    if key in carta_jugador:
                        del carta_jugador[key]


            return JsonResponse(carta_jugador)

        except CartasJugadore.DoesNotExist:
            return JsonResponse({"error": "Carta no encontrada"}, status=404)

        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al consultar la carta: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Operación no soportada"}, status=405)


def get_cartas(request):
    if request.method == "GET":
        try:
            cartas_query = CartasJugadore.objects.annotate(
                num_equipos=Count('equipos')
            ).filter(num_equipos=0).values()

            cartas_list = list(cartas_query)

            cartas_filtradas = []

            for carta_data in cartas_list:
                posicion = carta_data.get('posicion')

                carta_filtrada = carta_data.copy()

                if posicion == 'POR':
                    for key in ATRIBUTOS_JUGADOR:
                        if key in carta_filtrada:
                            del carta_filtrada[key]
                else:
                    for key in ATRIBUTOS_PORTERO:
                        if key in carta_filtrada:
                            del carta_filtrada[key]

                cartas_filtradas.append(carta_filtrada)
            return JsonResponse(cartas_filtradas, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al listar cartas: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Operación no soportada"}, status=405)


@csrf_exempt
def add_carta(request):
    if request.method == 'POST':
        try:
            jsonCarta = json.loads(request.body)
            nombre = jsonCarta.get('nombre')
            posicion = jsonCarta.get('posicion')

            if not nombre or not posicion:
                return JsonResponse({"error": "Los campos 'nombre' y 'posicion' son obligatorios."}, status=400)

            try:
                carta_existente = CartasJugadore.objects.get(nombre=nombre, esta_activa=False)


                carta_existente.esta_activa = True
                carta_existente.save(update_fields=['esta_activa'])

                return JsonResponse({
                    "mensaje": f"La carta '{nombre}' ya existía y ha sido reactivada (esta_activa=True).",
                    "id": carta_existente.id,
                    "media_actual": carta_existente.media
                })

            except CartasJugadore.DoesNotExist:
                pass
            jsonCarta.pop('equipo', None)
            jsonCarta.pop('equipo_id', None)
            jsonCarta.pop('media', None)


            if posicion == 'POR':
                for attr in ATRIBUTOS_JUGADOR:
                    jsonCarta.pop(attr, None)
            else:
                for attr in ATRIBUTOS_PORTERO:
                    jsonCarta.pop(attr, None)


            carta = CartasJugadore.objects.create(**jsonCarta)

            return JsonResponse({
                "mensaje": "Se ha insertado correctamente",
                "id": carta.id,
                "media_final": carta.media
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)
        except ValidationError as e:
            return JsonResponse(
                {"error": f"Error de validación: {e.message_dict if hasattr(e, 'message_dict') else e.message}"},status=400)
        except IntegrityError as e:
            return JsonResponse({"error": f"Error de integridad: Ya existe una carta activa con el nombre '{nombre}'."},status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al añadir la carta: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Operación no soportada"}, status=405)


@csrf_exempt
def update_carta(request, id):
    if request.method in ('PUT', 'PATCH'):
        try:
            carta = CartasJugadore.objects.get(id=id)
            data = json.loads(request.body)

            if carta.equipos.count() > 0:
                return JsonResponse({
                    "error": f"La carta con ID {id} está asignada a '{carta.equipos.count()}' equipo(s) y no puede ser actualizada."
                }, status=403)


            data.pop('id', None)
            data.pop('equipo', None)
            data.pop('equipo_id', None)
            data.pop('media', None)

            for key, value in data.items():
                setattr(carta, key, value)

            carta.save()

            response_data = {
                'id': carta.id,
                'nombre': carta.nombre,
                'pais': carta.pais,
                'posicion': carta.posicion,
                'liga': carta.liga,
                'esta_activa': carta.esta_activa,
                'media_nueva': carta.media,
                'mensaje_adicional': 'Las estadísticas se actualizaron correctamente'
            }

            return JsonResponse(response_data)

        except CartasJugadore.DoesNotExist:
            return JsonResponse({"error": "Carta no encontrada"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)
        except ValidationError as e:

            return JsonResponse({"error": f"Error de validación del modelo: {e.message_dict if hasattr(e, 'message_dict') else str(e)}"},status=400)
        except IntegrityError as e:
            return JsonResponse({"error": f"Error de integridad de datos: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al actualizar la carta: {str(e)}"}, status=500)

    else:
        return JsonResponse({"error": "Método no soportado. Usa PUT o PATCH."}, status=405)


@csrf_exempt
def activar_carta(request, id):
        if request.method == 'POST':
            try:
                carta = CartasJugadore.objects.get(id=id)

                if carta.equipos.count() > 0:
                    return JsonResponse({
                        "error": f"La carta con ID {id} está asignada a'{carta.equipos.count()}' equipo(s) y su estado activo no puede ser modificado."
                    }, status=403)

                if carta.esta_activa:
                    return JsonResponse({
                        "mensaje": f"La carta '{carta.nombre}' ya estaba activa. No se requiere ninguna acción."
                    }, status=200)


                carta.esta_activa = True
                carta.save(update_fields=['esta_activa'])


                return JsonResponse({
                    "mensaje": f"La carta '{carta.nombre}' ha sido ACTIVADA correctamente.",
                    "estado_activo": True
                })

            except CartasJugadore.DoesNotExist:
                return JsonResponse({"error": "Carta no encontrada"}, status=404)

            except Exception as e:
                return JsonResponse({"error": f"Error inesperado al activar la carta: {str(e)}"}, status=500)

        else:
            return JsonResponse({"error": "Método no soportado. Usa POST."}, status=405)


@csrf_exempt
def desactivar_carta(request, id):

    if request.method == 'POST':
        try:
            carta = CartasJugadore.objects.get(id=id)

            if carta.equipos.count() > 0:
                return JsonResponse({
                    "error": f"La carta con ID {id} está asignada a'{carta.equipos.count()}' equipo(s) y su estado activo no puede ser modificado."
                }, status=403)


            if not carta.esta_activa:
                return JsonResponse({
                    "mensaje": f"La carta '{carta.nombre}' ya estaba inactiva. No se requiere ninguna acción."
                }, status=200)


            carta.esta_activa = False

            carta.save(update_fields=['esta_activa'])

            return JsonResponse({
                "mensaje": f"La carta '{carta.nombre}' ha sido DESACTIVADA (borrado lógico) correctamente.",
                "estado_activo": False
            })

        except CartasJugadore.DoesNotExist:
            return JsonResponse({"error": "Carta no encontrada"}, status=404)

        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al desactivar la carta: {str(e)}"}, status=500)

    else:
        return JsonResponse({"error": "Método no soportado. Usa POST."}, status=405)

@csrf_exempt
@transaction.atomic
def asignar_equipo_servicio(request, usuario_id):

    if request.method == 'POST':
        try:

            try:
                usuario = Usuario.objects.get(pk=usuario_id)
            except Usuario.DoesNotExist:
                return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)

            if usuario.equipo is not None:
                return JsonResponse(
                    {'error': 'Este usuario ya tiene un equipo asociado. Debe eliminarse el equipo previamente.'},
                    status=400
                )

            cartas_libres = CartasJugadore.objects.filter(esta_activa=True)

            porteros_libres = []
            defensas_libres = []
            centrocampistas_libres = []
            delanteros_libres = []

            for carta in cartas_libres:
                tipo = carta.tipo_posicion
                if tipo == 'Portero':
                    porteros_libres.append(carta)
                elif tipo == 'Defensa':
                    defensas_libres.append(carta)
                elif tipo == 'Centrocampista':
                    centrocampistas_libres.append(carta)
                elif tipo == 'Delantero':
                    delanteros_libres.append(carta)

            min_por = 2
            min_def = 8
            min_cen = 6
            min_del = 5

            if (len(porteros_libres) < min_por or
                    len(defensas_libres) < min_def or
                    len(centrocampistas_libres) < min_cen or
                    len(delanteros_libres) < min_del):
                return JsonResponse(
                    {'error': 'No hay suficientes jugadores libres disponibles para crear un equipo completo.'},
                    status=409
                )

            num_por = random.randint(min_por, 3)
            num_def = random.randint(min_def, 10)
            num_cen = random.randint(min_cen, 9)
            num_del = random.randint(min_del, 6)

            total_jugadores = num_por + num_def + num_cen + num_del
            while not (23 <= total_jugadores <= 25):
                num_por = random.randint(min_por, 3)
                num_def = random.randint(min_def, 10)
                num_cen = random.randint(min_cen, 9)
                num_del = random.randint(min_del, 6)
                total_jugadores = num_por + num_def + num_cen + num_del

            nuevo_equipo = Equipo.objects.create(nombre=f"Equipo de {usuario.nombre}")

            usuario.equipo = nuevo_equipo
            usuario.save()

            cartas_seleccionadas = []
            cartas_seleccionadas.extend(random.sample(porteros_libres, num_por))
            cartas_seleccionadas.extend(random.sample(defensas_libres, num_def))
            cartas_seleccionadas.extend(random.sample(centrocampistas_libres, num_cen))
            cartas_seleccionadas.extend(random.sample(delanteros_libres, num_del))

            nuevo_equipo.cartas.add(*cartas_seleccionadas)

            return JsonResponse({
                'mensaje': '¡Equipo creado y asignado con éxito!',
                'equipo_id': nuevo_equipo.id,
                'nombre_equipo': nuevo_equipo.nombre,
                'propietario': usuario.nombre,
                'total_jugadores': total_jugadores,
                'composicion': {
                    'porteros': num_por,
                    'defensas': num_def,
                    'centrocampistas': num_cen,
                    'delanteros': num_del
                }
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al asignar el equipo: {str(e)}"}, status=500)

    else:
        return JsonResponse({"error": "Método no soportado. Usa POST."}, status=405)

@csrf_exempt
def get_equipo_usuario(request, usuario_id):
    if request.method == "GET":
        try:
            usuario = Usuario.objects.get(pk=usuario_id)

            if usuario.equipo is None:
                return JsonResponse({
                    "error": "Este usuario no tiene ningún equipo asignado."
                }, status=404)

            equipo = usuario.equipo

            cartas_del_equipo = equipo.cartas.filter(esta_activa=True).values()

            cartas_list = list(cartas_del_equipo)

            cartas_filtradas = []
            for carta_data in cartas_list:
                posicion = carta_data.get('posicion')
                carta_filtrada = carta_data.copy()

                if posicion == 'POR':
                    for key in ATRIBUTOS_JUGADOR:
                        if key in carta_filtrada:
                            del carta_filtrada[key]
                else:
                    for key in ATRIBUTOS_PORTERO:
                        if key in carta_filtrada:
                            del carta_filtrada[key]

                cartas_filtradas.append(carta_filtrada)

            response_data = {
                'propietario': usuario.nombre,
                'equipo_id': equipo.id,
                'nombre_equipo': equipo.nombre,
                'cartas_activas': cartas_filtradas
            }

            return JsonResponse(response_data, safe=False)

        except Usuario.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al consultar el equipo: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Operación no soportada. Usa GET."}, status=405)


@csrf_exempt
@transaction.atomic
def add_carta_to_equipo(request, id_equipo):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_carta = data.get('id_carta')

            if id_carta is None:
                return JsonResponse({"error": "Se requiere el 'id_carta' en el cuerpo de la solicitud."}, status=400)


            equipo = Equipo.objects.get(id=id_equipo)
            carta = CartasJugadore.objects.get(id=id_carta)


            if not carta.esta_activa:
                return JsonResponse(
                    {"error": f"La carta '{carta.nombre}' debe estar activa para poder ser asignada a un equipo."},status=400)


            if equipo.cartas.filter(id=id_carta).exists():
                return JsonResponse({
                    "error": f"La carta '{carta.nombre}' ya se encuentra asociada al equipo '{equipo.nombre}'."}, status=400)

            cartas_activas_actuales = list(equipo.cartas.filter(esta_activa=True))
            conteo_actual = len(cartas_activas_actuales)

            if conteo_actual >= LIMITES_EQUIPO['total']['max']:
                return JsonResponse({
                    "error": f"El equipo ya tiene el máximo de {LIMITES_EQUIPO['total']['max']} cartas activas asociadas. No se puede insertar esta carta."
                }, status=400)


            tipo_posicion_nueva = carta.tipo_posicion

            conteo_actual_tipo = sum(1 for c in cartas_activas_actuales if c.tipo_posicion == tipo_posicion_nueva)


            limite_maximo_tipo = LIMITES_EQUIPO[tipo_posicion_nueva]['max']

            if conteo_actual_tipo >= limite_maximo_tipo:
                return JsonResponse({
                    "error": f"No se puede asociar la carta '{carta.nombre}'. Ya se alcanzó el límite máximo de {limite_maximo_tipo} jugadores en la categoría '{tipo_posicion_nueva}'."
                }, status=400)

            equipo.cartas.add(carta)

            return JsonResponse({
                "mensaje": f"Carta '{carta.nombre}' ({carta.posicion}) asignada correctamente al equipo '{equipo.nombre}'.",
                "jugadores_totales_equipo": conteo_actual + 1,
                f"jugadores_en_{tipo_posicion_nueva}": conteo_actual_tipo + 1
            })

        except ObjectDoesNotExist as e:
            if "Equipo" in str(e):
                return JsonResponse({"error": f"Equipo con ID {id_equipo} no encontrado."}, status=404)
            else:
                return JsonResponse({"error": f"Carta con ID {id_carta} no encontrada."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error inesperado al añadir carta al equipo: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método no soportado. Usa POST."}, status=405)