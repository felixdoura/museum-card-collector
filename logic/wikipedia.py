"""
Módulo wikipedia.py

Este módulo consulta la API pública de Wikipedia en español para obtener
un extracto descriptivo sobre un museo dado su nombre.

Utilizado en la pantalla de selección de cartas para mostrar
información contextual sobre cada museo al jugador.

Nota: este componente también se instala con el requirements.txt, si instalaron una 
version anterior de la que compartí antes del 18/4 por mail es necesario
reinstalar los requerimientos para que no haya inconvenientes.
"""

import re
import requests

# URL base de la API de Wikipedia en español
_WIKIPEDIA_API = "https://es.wikipedia.org/api/rest_v1/page/summary/"

# Timeout en segundos para las peticiones HTTP
_TIMEOUT = 5

# Cache en memoria para no repetir consultas durante la sesión
_cache: dict[str, str] = {}


def _limpiar_texto(texto: str, max_chars: int = 280) -> str:
    """
    Limpia y recorta el extracto de Wikipedia para mostrarlo en la GUI.

    Elimina referencias entre paréntesis vacíos, espacios duplicados
    y recorta al límite de caracteres indicado.

    Devuelve el texto lo mas limpio y ordenado posible
    """
    # A veces la API deja algunos parentesis vacios, esos los borramos con la siguiente linea
    texto = re.sub(r'\(\s*\)', '', texto)
    # Lo mismo con espacios multiples, puede pasar que se escriban varias veces espacios vacios
    texto = re.sub(r' {2,}', ' ', texto).strip()

    if len(texto) > max_chars:
        # Esto recorta el ultimo espacio antes de llegar al limite de caracteres
        texto = texto[:max_chars].rsplit(' ', 1)[0] + "..."

    return texto


def obtener_extracto(nombre_museo: str) -> str:
    """
    Obtiene un extracto descriptivo de Wikipedia sobre el museo indicado.

    Primero busca en el cache de la sesión. Si no está, realiza la
    consulta HTTP a la API de Wikipedia en español.
    """
    # Verificar cache primero
    if nombre_museo in _cache:
        return _cache[nombre_museo]

    try:
        # Formatear el nombre para la URL
        titulo = nombre_museo.replace(" ", "_")
        url = _WIKIPEDIA_API + titulo

        respuesta = requests.get(url, timeout=_TIMEOUT, headers={"Accept": "application/json"})

        if respuesta.status_code == 200:
            datos = respuesta.json()
            extracto = datos.get("extract", "")

            if extracto:
                resultado = _limpiar_texto(extracto)
                _cache[nombre_museo] = resultado
                return resultado

        # Si el programa no encuentra el articulo en español, lo busca en inglés
        return _fallback_ingles(nombre_museo)

    except requests.exceptions.Timeout:
        return "No se pudo conectar a Wikipedia"
    except requests.exceptions.ConnectionError:
        return "Sin conexión a internet"
    except Exception:
        return "Información no disponible en este momento."


def _fallback_ingles(nombre_museo: str) -> str:
    """
    Esta parte del código es la que intenta abrir el extracto del articulo cuando haya
    sido encontrado en ingles.
    """
    try:
        api_en = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        titulo = nombre_museo.replace(" ", "_")
        respuesta = requests.get(api_en + titulo, timeout=_TIMEOUT, headers={"Accept": "application/json"})
        if respuesta.status_code == 200:
            datos = respuesta.json()
            extracto = datos.get("extract", "")
            if extracto:
                return _limpiar_texto(extracto)
    except Exception:
        pass
    return "Información no disponible para este museo."


def limpiar_cache() -> None:
    """Vacía el cache de extractos de la sesión actual."""
    _cache.clear()
