"""
--------------
Esta carpeta tiene las clases del juego. Por ahora lo pensé como algo sencillo que tenga estas dos clases, yo no sé si el día de mañana se nos ocurre
agregar mas cosas locas. También había pensado en un momento si se podría armar algo estilo que por ejemplo tengas que estar físicamente en un museo
para poder coleccionar esa carta y luego puedas armar una especie de album de figuritas donde puedas cambiar las cartas con otra persona que haya estado
en un museo diferente en otra parte del mundo (no se, es algo para pensar en el futuro).

Está separada en dos módulos que se separan de la siguiente forma (por ahora):
    - carta: Clase abstracta Carta y sus dos subclases CartaNormal, CartaEspecial.
    - jugador: Clase Jugador con perfil, puntaje y colección.
"""

from models.carta import Carta, CartaNormal, CartaEspecial
from models.jugador import Jugador

__all__ = ["Carta", "CartaNormal", "CartaEspecial", "Jugador"]
