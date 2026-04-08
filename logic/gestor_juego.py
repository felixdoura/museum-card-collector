"""
Módulo gestor_juego.py
----------------------
Implementa la lógica principal del juego Museum Card Collector.
Gestiona la carga de cartas, las rondas de preguntas mediante una queue,
y el desbloqueo de cartas al responder correctamente.

Clases:
    - GestorJuego: Orquesta el flujo completo de una partida.
"""

import json
import os
import random
from queue import Queue

from models.carta import Carta, CartaNormal, CartaEspecial
from models.jugador import Jugador
from logic.crud import actualizar_jugador

# Rutas a los archivos de datos
_BASE = os.path.dirname(__file__)
RUTA_CARTAS     = os.path.join(_BASE, "..", "data", "cartas.json")
RUTA_PREGUNTAS  = os.path.join(_BASE, "..", "data", "preguntas.json")


class GestorJuego:
    """
    Orquesta el flujo completo del juego: carga de cartas, rondas
    de preguntas y desbloqueo de cartas para un jugador.

    Atributos:
        jugador (Jugador): Jugador activo en la sesión.
        cartas (list[Carta]): Lista de todas las cartas disponibles en el juego.
        _preguntas_db (dict): Base de datos de preguntas indexada por país.
        _cola_preguntas (Queue): Cola de preguntas de la ronda activa.
        _carta_activa (Carta | None): Carta que se está intentando desbloquear.
        _aciertos_ronda (int): Contador de respuestas correctas en la ronda actual.
    """

    def __init__(self, jugador: Jugador):
        """
        Inicializa el gestor con el jugador activo y carga los datos del juego.
        El argumento es el jugador que está en ese momento en el juego
        """
        self.jugador = jugador
        self.cartas: list[Carta] = []
        self._preguntas_db: dict = {}
        self._cola_preguntas: Queue = Queue()
        self._carta_activa: Carta | None = None
        self._aciertos_ronda: int = 0

        # Cargar datos al inicializar
        self._cargar_cartas()
        self._cargar_preguntas()

    def _cargar_cartas(self) -> None:
        """
        Carga las cartas desde cartas.json e instancia los objetos
        CartaNormal o CartaEspecial dpeendiendo lo que haga falta en ese momento.
        """
        with open(RUTA_CARTAS, "r", encoding="utf-8") as f:
            datos = json.load(f)

        for d in datos:
            if d["dificultad"] == "especial":
                carta = CartaEspecial(
                    nombre=d["nombre"],
                    museo=d["museo"],
                    pais=d["pais"],
                    imagen_path=d["imagen_path"],
                    dato_curioso=d.get("dato_curioso", "")
                )
            else:
                carta = CartaNormal(
                    nombre=d["nombre"],
                    museo=d["museo"],
                    pais=d["pais"],
                    imagen_path=d["imagen_path"]
                )
            self.cartas.append(carta)

    def _cargar_preguntas(self) -> None:
        """
        Carga el banco de preguntas desde preguntas.json.
        Se indexa por el nombre del pais en este punto.
        """
        with open(RUTA_PREGUNTAS, "r", encoding="utf-8") as f:
            self._preguntas_db = json.load(f)

    def get_cartas_disponibles(self) -> list[Carta]:
        """
        Retorna las cartas que el jugador aún no ha desbloqueado.
        """
        return [c for c in self.cartas if not self.jugador.tiene_carta(c.nombre)]

    def get_cartas_desbloqueadas(self) -> list[Carta]:
        """
        Retorna las cartas que el jugador ya tiene en su colección.
        """
        return [c for c in self.cartas if self.jugador.tiene_carta(c.nombre)]

    def get_carta_por_nombre(self, nombre: str) -> Carta | None:
        """
        Busca una carta por su nombre en la lista de cartas del juego.
        El argumento es el nombre de la carta, retorna el nombre si la encuentra y none si no existe
        """
        for carta in self.cartas:
            if carta.nombre == nombre:
                return carta
        return None

    def iniciar_ronda(self, carta: Carta) -> bool:
        """
        Prepara una nueva ronda de preguntas para intentar desbloquear la carta indicada. Carga las preguntas del país correspondiente
        en la queue, mezcladas y en cantidad según la dificultad de la carta. El argumento es la carta que el jugador quiere desbloquear
        """
        preguntas_pais = self._preguntas_db.get(carta.pais)
        if not preguntas_pais:
            return False

        self._carta_activa = carta
        self._aciertos_ronda = 0

        # Vaciar la cola antes de cargar nuevas preguntas
        while not self._cola_preguntas.empty():
            self._cola_preguntas.get()

        # Seleccionar y mezclar preguntas según dificultad
        cantidad = carta.get_preguntas_requeridas()
        seleccionadas = random.sample(preguntas_pais, min(cantidad, len(preguntas_pais)))

        for pregunta in seleccionadas:
            # Mezclar las opciones para que la respuesta no siempre esté en la misma posición, sino se volvería un poco monótono y no tiene sentido
            opciones = pregunta["opciones"][:]
            random.shuffle(opciones)
            self._cola_preguntas.put({
                "pregunta": pregunta["pregunta"],
                "opciones": opciones,
                "respuesta": pregunta["respuesta"]
            })

        return True

    def hay_siguiente_pregunta(self) -> bool:
        """
        Indica si quedan preguntas en la cola de la ronda activa.
        """
        return not self._cola_preguntas.empty()

    def get_siguiente_pregunta(self) -> dict | None:
        """
        Extrae y retorna la siguiente pregunta de la cola.
        """
        if self._cola_preguntas.empty():
            return None
        return self._cola_preguntas.get()

    def responder(self, pregunta: dict, respuesta_usuario: str) -> bool:
        """
        Evalúa la respuesta del usuario para una pregunta dada.
        Si es correcta, suma puntos al jugador.
        """
        es_correcta = respuesta_usuario.strip() == pregunta["respuesta"].strip()

        if es_correcta:
            self._aciertos_ronda += 1
            self.jugador.sumar_puntos(Jugador.PUNTOS_POR_RESPUESTA)

        return es_correcta

    def finalizar_ronda(self) -> dict:
        """
        Cierra la ronda activa, evalúa si el jugador desbloqueó la carta
        y guarda el progreso automáticamente en el JSON.
        """
        self.jugador.registrar_partida()
        carta_desbloqueada = False

        if self._carta_activa is not None:
            requeridos = self._carta_activa.get_preguntas_requeridas()

            if self._aciertos_ronda >= requeridos:
                self.jugador.agregar_carta(self._carta_activa)
                carta_desbloqueada = True

        # Persistir progreso automáticamente. No hace falta guardar una partida sino que está pensado para que lo haga automáticamente
        actualizar_jugador(self.jugador)

        resultado = {
            "carta_desbloqueada": carta_desbloqueada,
            "aciertos": self._aciertos_ronda,
            "requeridos": self._carta_activa.get_preguntas_requeridas() if self._carta_activa else 0,
            "carta": self._carta_activa
        }

        # Resetear estado de la ronda
        self._carta_activa = None
        self._aciertos_ronda = 0

        return resultado

    def get_progreso(self) -> dict:
        """
        Retorna un resumen del progreso actual del jugador.
        """
        total = len(self.cartas)
        desbloqueadas = self.jugador.total_cartas()
        porcentaje = round((desbloqueadas / total) * 100, 1) if total > 0 else 0.0

        return {
            "total_cartas": total,
            "cartas_desbloqueadas": desbloqueadas,
            "cartas_restantes": total - desbloqueadas,
            "porcentaje": porcentaje
        }
