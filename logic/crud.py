"""
Módulo de creacion
--------------
Funciones:
    - crear_jugador: Agrega un nuevo jugador al archivo JSON.
    - leer_jugador: Obtiene un jugador por nombre.
    - leer_todos: Retorna la lista completa de jugadores.
    - actualizar_jugador: Actualiza los datos de un jugador existente.
    - eliminar_jugador: Elimina un jugador del archivo JSON.
    - jugador_existe: Verifica si un jugador ya está registrado.
"""

import json
import os
from models.jugador import Jugador

# Ruta al archivo de persistencia, esto es relativo al archivo del juego, me tengo que fijar bien el nombre de la ruta, si la cambio puede romper basicamente todo
RUTA_JUGADORES = os.path.join(os.path.dirname(__file__), "..", "data", "jugadores.json")

def _leer_archivo() -> list[dict]:
    """
    Lee el archivo jugadores.json y va a retornar una lista (y si, obvio, es no relacional jaja)
    """
    if not os.path.exists(RUTA_JUGADORES):
        return []
    with open(RUTA_JUGADORES, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _escribir_archivo(jugadores: list[dict]) -> None:
    """
    Escribe la lista de jugadores en el archivo jugadores.json.
    """
    with open(RUTA_JUGADORES, "w", encoding="utf-8") as f:
        json.dump(jugadores, f, ensure_ascii=False, indent=2)

def crear_jugador(jugador: Jugador) -> bool:
    """
    Agrega un nuevo jugador al archivo JSON.
    bool: True si se creó correctamente, False si el nombre ya existe.
    """
    jugadores = _leer_archivo()

    # Chequear que no exista un jugador con el mismo nombre
    if any(j["nombre"] == jugador.nombre for j in jugadores):
        return False

    jugadores.append(jugador.to_dict())
    _escribir_archivo(jugadores)
    return True

def leer_jugador(nombre: str) -> Jugador | None:
    """
    Busca y retorna un jugador por su nombre.
    Jugador | None: Instancia del jugador si existe, None si no se encuentra.
    """
    jugadores = _leer_archivo()
    for j in jugadores:
        if j["nombre"] == nombre:
            return Jugador.from_dict(j)
    return None


def leer_todos() -> list[Jugador]:
    """
    Retorna la lista completa de jugadores registrados.
    """
    jugadores = _leer_archivo()
    return [Jugador.from_dict(j) for j in jugadores]


def leer_ranking() -> list[Jugador]:
    """
    Retorna la lista de jugadores ordenada por puntaje descendente. (detalle en el reverse=true, si quisiera cambiar el orden de como lo mostramos es acá)
    """
    todos = leer_todos()
    return sorted(todos, key=lambda j: j.puntaje, reverse=True)

def actualizar_jugador(jugador: Jugador) -> bool:
    """
    Actualiza los datos de un jugador existente en el archivo JSON.
    Identifica al jugador por su nombre.

    bool: True si se actualizó correctamente, False si no se encontró.
    """
    jugadores = _leer_archivo()

    for i, j in enumerate(jugadores):
        if j["nombre"] == jugador.nombre:
            jugadores[i] = jugador.to_dict()
            _escribir_archivo(jugadores)
            return True

    return False

def eliminar_jugador(nombre: str) -> bool:
    """
    Elimina un jugador del archivo JSON por su nombre.
    bool: True si se eliminó correctamente, False si no se encontró. No hay forma de recuperar un jugador eliminado.
    """
    jugadores = _leer_archivo()
    nuevos = [j for j in jugadores if j["nombre"] != nombre]

    if len(nuevos) == len(jugadores):
        return False  # No se encontró el jugador

    _escribir_archivo(nuevos)
    return True

def jugador_existe(nombre: str) -> bool:
    """
    Verifica si un jugador con ese nombre ya está registrado.
    bool: True si existe, False si no.
    """
    jugadores = _leer_archivo()
    return any(j["nombre"] == nombre for j in jugadores)
