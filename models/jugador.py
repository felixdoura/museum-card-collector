"""
En este archivo se define la clase Jugador que representa a un usuario del juego. Igual que como hice en el archivo carta.py, prefiero hacer las aclaraciones en la primera parte
para despues reducir un poco los comentarios que estan entre lineas.

Hoy por hoy puede haber una sola clase, pero si existieran varios tipos de jugadores podría agregarlos acá como sub clases, por ejemplo si alguien consigue varias cartas
podría pasar a un tier mayor o algo así.

Clases:
    - Jugador: gestiona el perfil, puntaje y colección de cartas del usuario.

        Atributos:
            nombre (str): Nombre del jugador (identificador único).
            puntaje (int): Puntaje acumulado a lo largo de las partidas.
            coleccion (list[str]): Lista de nombres de cartas desbloqueadas.
            partidas_jugadas (int): Cantidad de rondas completadas.
            fecha_registro (str): Fecha de creación del perfil.
        
        Args:
            nombre (str): Nombre del jugador.
            puntaje (int): Puntaje inicial (default 0).
            coleccion (list): Lista de cartas desbloqueadas (default []).
            partidas_jugadas (int): Partidas previas (default 0).
            fecha_registro (str): Fecha ISO; si es None, se usa la fecha actual.
"""

from datetime import datetime
from models.carta import Carta


class Jugador:
    PUNTOS_POR_RESPUESTA = 10   # Puntos por cada respuesta correcta
    PUNTOS_BONUS_CARTA   = 50   # Bonus al desbloquear una carta normal
    PUNTOS_BONUS_ESPECIAL = 100  # Bonus al desbloquear una carta especial

    def __init__(self, nombre: str, puntaje: int = 0,
                 coleccion: list = None, partidas_jugadas: int = 0,
                 fecha_registro: str = None):
        """
        Inicializa un jugador con sus atributos de perfil.
        """
        self.nombre = nombre
        self.puntaje = puntaje
        self.coleccion = coleccion if coleccion is not None else []
        self.partidas_jugadas = partidas_jugadas
        self.fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Colección

    def agregar_carta(self, carta: Carta) -> bool:
        """
        Agrega una carta a la colección del jugador si no la tiene.

        Args:
            carta (Carta): Instancia de carta a agregar. (estos vienen desde la clase directamente)

        Returns:
            bool: True si se agregó correctamente, False si ya la tenía.
        """
        if carta.nombre not in self.coleccion:
            self.coleccion.append(carta.nombre)
            # Otorgar bonus según tipo de carta
            bonus = (self.PUNTOS_BONUS_ESPECIAL
                     if carta.dificultad == "especial"
                     else self.PUNTOS_BONUS_CARTA)
            self.puntaje += bonus
            return True
        return False

    def tiene_carta(self, nombre_carta: str) -> bool:
        """
        Aca se chequea si el jugador tiene la carta o todavía no.

        Args:
            nombre_carta (str): Nombre de la carta a verificar.

        Returns:
            bool: True si la tiene, False si no.
        """
        return nombre_carta in self.coleccion

    def total_cartas(self) -> int:
        """Retorna la cantidad total de cartas en la colección."""
        return len(self.coleccion)

    # Puntaje

    def sumar_puntos(self, cantidad: int) -> None:
        """
        Suma puntos al puntaje del jugador.

        Args:
            cantidad (int): Cantidad de puntos a sumar. Debe ser un numero entero positivo.

        Raises:
            ValueError: Si la cantidad es negativa, por definición mía el jugador no puede tener puntos negativos (o si, no se jaja podría algun dia perder cartas el jugador??)
        """
        if cantidad < 0:
            raise ValueError("La cantidad de puntos no puede ser negativa.")
        self.puntaje += cantidad

    def registrar_partida(self) -> None:
        """Incrementa el contador de partidas jugadas en 1."""
        self.partidas_jugadas += 1

    # Series

    def to_dict(self) -> dict:
        """
        Serializa el jugador a un diccionario para persistencia en json.

        Returns:
            dict: Representación del jugador como diccionario.
        """
        return {
            "nombre": self.nombre,
            "puntaje": self.puntaje,
            "coleccion": self.coleccion,
            "partidas_jugadas": self.partidas_jugadas,
            "fecha_registro": self.fecha_registro
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Jugador":
        """
        Crea una instancia de Jugador a partir de un diccionario (viene desde el json).

        Args:
            data (dict): Diccionario con los datos del jugador.

        Returns:
            Jugador: Nueva instancia reconstruida desde los datos.
        """
        return cls(
            nombre=data["nombre"],
            puntaje=data.get("puntaje", 0),
            coleccion=data.get("coleccion", []),
            partidas_jugadas=data.get("partidas_jugadas", 0),
            fecha_registro=data.get("fecha_registro")
        )

    # Representación

    def __str__(self) -> str:
        """Retorna una representación del jugador."""
        return (f"Jugador: {self.nombre} | "
                f"Puntaje: {self.puntaje} | "
                f"Cartas: {self.total_cartas()} | "
                f"Partidas: {self.partidas_jugadas}")

    def __repr__(self) -> str:
        """Retorna una representación técnica del jugador."""
        return (f"Jugador(nombre={self.nombre!r}, puntaje={self.puntaje}, "
                f"cartas={self.total_cartas()})")
