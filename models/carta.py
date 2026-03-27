"""
En esta primera parte del documento voy a estar contando los tipos de clases, atributos y argumentos, pensé en hacerlo de esta forma porque me parecía mas prolijo
a la hora de comentar y explicar el codigo. Quizá una mejor forma hubiese sido armar un documento aparte con el diccionario, pero para el alcance de este proyecto
quizás de esta forma era suficiente, en cualquier caso aguardo feedback.

También agrego que voy a estar comentando las partes donde se haga actualizaciones de los argumentos o de algunos métodos.

Clases y subclases:
    - Carta: clase base con atributos comunes y el método de es abstracto porque es la clase padre.
            Atributos en esta clase:
                nombre (str): Nombre de la carta.
                museo (str): Nombre del museo representado.
                pais (str): País donde se encuentra el museo.
                dificultad (str): Nivel de dificultad para desbloquear la carta.
                __imagen_path (str): Ruta a la imagen de la carta (encapsulado).
            
            Args:
                nombre (str): Nombre identificador de la carta.
                museo (str): Nombre del museo representado.
                pais (str): País de origen del museo.
                dificultad (str): Nivel de dificultad ('normal' o 'especial').
                imagen_path (str): Ruta relativa a la imagen de la carta.

    - CartaNormal: carta estándar desbloqueable respondiendo 5 preguntas.
            Atributos:
                Hereda de la clase Carta

            Args:
                nombre (str): Nombre identificador de la carta.
                museo (str): Nombre del museo representado.
                pais (str): País de origen del museo.
                imagen_path (str): Ruta relativa a la imagen de la carta.
            
    - CartaEspecial: carta rara de mayor dificultad, aplica polimorfismo (tengo que remarcar que es un polimorfismo de herencia y no de sobrecarga, lo aclaro por las dudas).
            Atributos:
                Hereda de la clase Carta

            Args:
                nombre (str): Nombre identificador de la carta.
                museo (str): Nombre del museo representado.
                pais (str): País de origen del museo.
                imagen_path (str): Ruta relativa a la imagen de la carta.
                dato_curioso (str): Dato adicional sobre el museo (opcional).
"""

from abc import ABC, abstractmethod


class Carta(ABC):
    def __init__(self, nombre: str, museo: str, pais: str,
                 dificultad: str, imagen_path: str):
        """
        La carta arranca con los atributos principales
        """
        self.nombre = nombre
        self.museo = museo
        self.pais = pais
        self.dificultad = dificultad
        self.__imagen_path = imagen_path  # Atributo encapsulado

    # ── Getter y setter para el atributo encapsulado ──────────────────────

    def get_imagen_path(self) -> str:
        """Retorna la ruta de la imagen de la carta."""
        return self.__imagen_path

    def set_imagen_path(self, nueva_ruta: str) -> None:
        """
        Actualiza la ruta de la imagen de la carta.

        Args:
            nueva_ruta (str): Nueva ruta relativa a la imagen.

        Raises:
            ValueError: Si la ruta está vacía.
        """
        if not nueva_ruta.strip():
            raise ValueError("La ruta de imagen no puede estar vacía.")
        self.__imagen_path = nueva_ruta

    # Metodo abstactro

    @abstractmethod
    def get_descripcion(self) -> str:
        """
        Retorna una descripción de la carta y debe ser implementado por cada subclase. 

        Returns:
            str: Descripción de la carta.
        """
        pass

    # Representación

    def __str__(self) -> str:
        """Retorna una representación que pueda leerse de la carta."""
        return f"[{self.dificultad.upper()}] {self.nombre} — {self.museo} ({self.pais})"

    def __repr__(self) -> str:
        """Retorna una representación que sea un poco mas técnica de la carta."""
        return (f"Carta(nombre={self.nombre!r}, museo={self.museo!r}, "
                f"pais={self.pais!r}, dificultad={self.dificultad!r})")

    def to_dict(self) -> dict:
        """
        Serializa la carta a un diccionario. Esto es para que sea mas util guardarlo en un json

        Returns:
            dict: Representación de la carta como diccionario.
        """
        return {
            "nombre": self.nombre,
            "museo": self.museo,
            "pais": self.pais,
            "dificultad": self.dificultad,
            "imagen_path": self.__imagen_path
        }


class CartaNormal(Carta):
    PREGUNTAS_REQUERIDAS = 5  # Constante de clase. Por ahora lo mantengo en 5, pero quien sabe si esto pueda cambiar (muy facil? muy dificil?)

    def __init__(self, nombre: str, museo: str, pais: str, imagen_path: str):
        """
        Inicializa una carta normal con dificultad fija 'normal'.
        """
        super().__init__(nombre, museo, pais, "normal", imagen_path)

    def get_descripcion(self) -> str:
        """
        Retorna la descripción de una carta normal.

        Returns:
            str: Descripción con información de como se desbloquea.
        """
        return (f"Carta Normal: {self.museo}, ubicado en {self.pais}. "
                f"Respondé {self.PREGUNTAS_REQUERIDAS} preguntas correctas para desbloquearla.")

    def get_preguntas_requeridas(self) -> int:
        """Retorna la cantidad de preguntas necesarias para desbloquear."""
        return self.PREGUNTAS_REQUERIDAS


class CartaEspecial(Carta):
    PREGUNTAS_REQUERIDAS = 7  # Más difícil que CartaNormal

    def __init__(self, nombre: str, museo: str, pais: str,
                 imagen_path: str, dato_curioso: str = ""):
        """
        Inicializa una carta especial con dificultad 'especial'.
        """
        super().__init__(nombre, museo, pais, "especial", imagen_path)
        self.dato_curioso = dato_curioso

    def get_descripcion(self) -> str:
        """
        Retorna la descripción extendida de una carta especial,
        incluyendo el dato curioso y la mayor dificultad requerida.

        Returns:
            str: Descripción completa con dato curioso y requisito de desbloqueo.
        """
        base = (f"★ Carta Especial: {self.museo}, ubicado en {self.pais}. "
                f"Necesitás {self.PREGUNTAS_REQUERIDAS} respuestas correctas para desbloquearla.")
        if self.dato_curioso:
            base += f" Dato curioso: {self.dato_curioso}"
        return base

    def get_preguntas_requeridas(self) -> int:
        """Retorna la cantidad de preguntas necesarias para desbloquear."""
        return self.PREGUNTAS_REQUERIDAS

    def to_dict(self) -> dict:
        """
        Extiende la serialización base agregando el dato curioso.

        Returns:
            dict: Representación extendida de la carta especial.
        """
        d = super().to_dict()
        d["dato_curioso"] = self.dato_curioso
        return d
