"""
Implementa la interfaz gráfica completa del juego Museum Card Collector
utilizando Pygame. Contiene todas las pantallas del juego separadas
de la lógica de negocio.

Pantallas implementadas:
    - PantallaLogin:      Ingreso o creación de perfil de jugador.
    - PantallaMenu:       Menú principal con puntaje y progreso.
    - PantallaCartas:     Selección de carta a desbloquear.
    - PantallaRonda:      Ronda de preguntas con opciones múltiples.
    - PantallaResultado:  Resultado al finalizar una ronda.
    - PantallaColeccion:  Visualización de cartas desbloqueadas.
    - PantallaRanking:    Ranking de jugadores por puntaje.
    - Interfaz:           Controlador principal que orquesta las pantallas.
"""

import pygame
import sys
import requests
from models.jugador import Jugador
from logic.crud import (crear_jugador, leer_jugador, jugador_existe, leer_ranking, eliminar_jugador)
from logic.gestor_juego import GestorJuego
from logic.wikipedia import obtener_extracto

"""Inicio del juego"""
pygame.init()
pygame.mixer.init()

"""Constantes para el tamaño de la pantalla"""
ANCHO  = 1000
ALTO   = 700
FPS    = 60
TITULO = "Museum Card Collector"

"""Definición de la paleta de colores (yo vengo del palo de Javascript/CSS/HTML, esto me cuesta bastante jaja ni hablar cuando aparece Tailwinds o Bootstrap)"""
NEGRO       = (10,  10,  15)
FONDO       = (15,  18,  28)
FONDO_PANEL = (22,  27,  45)
FONDO_CARTA = (28,  34,  55)
DORADO      = (212, 175, 55)
DORADO_CLARO= (240, 210, 100)
DORADO_OSC  = (140, 110, 30)
BLANCO      = (240, 238, 230)
GRIS_CLARO  = (160, 158, 150)
GRIS_OSC    = (60,  62,  75)
AZUL_ACC    = (80,  140, 200)
VERDE_ACC   = (60,  180, 100)
ROJO_ACC    = (200, 70,  70)
ESPECIAL    = (180, 130, 220)
TRANSPARENTE= (0,   0,   0,  0)

"""Definicion de las fuentes que voy a usar"""
def _cargar_fuentes():
    """Carga y retorna el diccionario de fuentes del juego."""
    return {
        "titulo":    pygame.font.SysFont("Georgia",       52, bold=True),
        "subtitulo": pygame.font.SysFont("Georgia",       28, bold=True),
        "h2":        pygame.font.SysFont("Georgia",       22, bold=True),
        "cuerpo":    pygame.font.SysFont("Trebuchet MS",  17),
        "cuerpo_b":  pygame.font.SysFont("Trebuchet MS",  17, bold=True),
        "pequeña":   pygame.font.SysFont("Trebuchet MS",  13),
        "mono":      pygame.font.SysFont("Courier New",   15),
        "grande":    pygame.font.SysFont("Georgia",       72, bold=True),
    }

FUENTES = _cargar_fuentes()


"""Ayudas para el modelado de los dibujos"""

def dibujar_texto(surface, texto, fuente, color, x, y, centrado=False, max_ancho=None):
    """
    Dibuja texto en la superficie dada, con soporte para centrado y
    truncado automático si se especifica un ancho máximo.

    Los argumentos van a ser la superficie, el texto, la fuente, el color, las posiciones, el centrado (en tipo booleano) y el maximo que se pueda modificar el ancho
    """
    if max_ancho:
        while fuente.size(texto)[0] > max_ancho and len(texto) > 3:
            texto = texto[:-4] + "..."
    img = fuente.render(texto, True, color)
    rect = img.get_rect()
    if centrado:
        rect.centerx = x
    else:
        rect.x = x
    rect.y = y
    surface.blit(img, rect)


def dibujar_rect_redondeado(surface, color, rect, radio=10, borde=0, color_borde=None):
    """
    Dibuja un rectángulo con esquinas redondeadas, opcionalmente con borde.
    """
    pygame.draw.rect(surface, color, rect, border_radius=radio)
    if borde and color_borde:
        pygame.draw.rect(surface, color_borde, rect, borde, border_radius=radio)


def dibujar_linea_dorada(surface, x1, y1, x2, y2, grosor=1):
    """Dibuja una linea para decorar que va a ser color dorado."""
    pygame.draw.line(surface, DORADO_OSC, (x1, y1), (x2, y2), grosor)


def dibujar_fondo(surface):
    """
    Dibuja el fondo general del juego
    """
    surface.fill(FONDO)
    # Lineas decorativas horizontales
    for i in range(0, ALTO, 60):
        pygame.draw.line(surface, (20, 24, 38), (0, i), (ANCHO, i), 1)
    # Marco dorado exterior
    pygame.draw.rect(surface, DORADO_OSC, (8, 8, ANCHO - 16, ALTO - 16), 1)
    pygame.draw.rect(surface, (30, 36, 58), (12, 12, ANCHO - 24, ALTO - 24), 1)


def dibujar_encabezado(surface, titulo, subtitulo=""):
    """
    Dibuja el encabezado de una pantalla con título y subtítulo opcionales.
    """
    dibujar_texto(surface, titulo, FUENTES["subtitulo"], DORADO, ANCHO // 2, 30, centrado=True)
    dibujar_linea_dorada(surface, 60, 68, ANCHO - 60, 68, 2)
    dibujar_linea_dorada(surface, 60, 72, ANCHO - 60, 72, 1)
    if subtitulo:
        dibujar_texto(surface, subtitulo, FUENTES["pequeña"], GRIS_CLARO, ANCHO // 2, 80, centrado=True)


"""Definición de la clase boton"""

class Boton:
    """
    Representa un botón interactivo de la interfaz gráfica.

    Los atributos de los botones van a ser el area donde se pueda clickear, el texto, color cuando hacer el hover, el color base y si está activo
    """

    def __init__(self, x, y, ancho, alto, texto, color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=BLANCO, radio=8):
        """
        Inicializa un botón con su posición, tamaño y colores.
        """
        self.rect        = pygame.Rect(x, y, ancho, alto)
        self.texto       = texto
        self.color_base  = color_base
        self.color_hover = color_hover
        self.color_texto = color_texto
        self.radio       = radio
        self.hover       = False
        self.activo      = True

    def dibujar(self, surface):
        """
        Dibuja el botón en la superficie, reflejando su estado (hover o normal).
        """
        color = self.color_hover if self.hover else self.color_base
        dibujar_rect_redondeado(surface, color, self.rect, self.radio, borde=1, color_borde=DORADO_OSC)
        cx = self.rect.centerx
        cy = self.rect.centery - FUENTES["cuerpo_b"].get_height() // 2
        dibujar_texto(surface, self.texto, FUENTES["cuerpo_b"], self.color_texto, cx, cy, centrado=True)

    def actualizar(self, pos_mouse):
        """
        Actualiza el estado hover del botón según la posición del mouse.
        """
        self.hover = self.rect.collidepoint(pos_mouse) and self.activo

    def fue_clickeado(self, evento):
        """
        Verifica si el botón fue clickeado.
        """
        return (self.activo and evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos))


"""Definicion del campo de texto"""

class CampoTexto:
    """
    Campo de entrada de texto interactivo para la interfaz.
    """

    def __init__(self, x, y, ancho, alto, placeholder="", max_chars=20):
        """
        Inicializa el campo de texto.
        """
        self.rect        = pygame.Rect(x, y, ancho, alto)
        self.texto       = ""
        self.placeholder = placeholder
        self.activo      = False
        self.max_chars   = max_chars
        self._cursor_vis = True
        self._cursor_timer = 0

    def manejar_evento(self, evento):
        """
        Procesa eventos de teclado y mouse para el campo de texto. Basicamente lo que esto permite es poder teclear y que escribas el nombre o incluso
        poder darle enter y que funcione como clickear el boton
        """
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.activo = self.rect.collidepoint(evento.pos)
        if evento.type == pygame.KEYDOWN and self.activo:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif evento.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.texto) < self.max_chars:
                    self.texto += evento.unicode

    def actualizar(self, dt):
        """
        Actualiza el parpadeo del cursor
        """
        self._cursor_timer += dt
        if self._cursor_timer >= 500:
            self._cursor_vis = not self._cursor_vis
            self._cursor_timer = 0

    def dibujar(self, surface):
        """
        Dibuja el campo de texto con su estado actual.
        """
        color_borde = DORADO if self.activo else DORADO_OSC
        dibujar_rect_redondeado(surface, FONDO_CARTA, self.rect, radio=6, borde=2, color_borde=color_borde)
        if self.texto:
            dibujar_texto(surface, self.texto, FUENTES["cuerpo"], BLANCO, self.rect.x + 12, self.rect.y + 10)
            if self.activo and self._cursor_vis:
                ancho_txt = FUENTES["cuerpo"].size(self.texto)[0]
                cx = self.rect.x + 12 + ancho_txt + 2
                cy1 = self.rect.y + 8
                cy2 = self.rect.y + self.rect.height - 8
                pygame.draw.line(surface, DORADO, (cx, cy1), (cx, cy2), 2)
        else:
            if self.activo and self._cursor_vis:
                pygame.draw.line(surface, DORADO, (self.rect.x + 12, self.rect.y + 8), (self.rect.x + 12, self.rect.y + self.rect.height - 8), 2)
            else:
                dibujar_texto(surface, self.placeholder, FUENTES["cuerpo"], GRIS_OSC, self.rect.x + 12, self.rect.y + 10)


"""Definicion de la clase pantalla"""

class Pantalla:
    """
    Clase base para todas las pantallas del juego. Define la interfaz que cada pantalla debe implementar.
    """

    def __init__(self, surface):
        self.surface  = surface
        self.siguiente = None  # Nombre de la siguiente pantalla a mostrar

    def manejar_eventos(self, eventos):
        """Procesa la lista de eventos de Pygame."""
        pass

    def actualizar(self, dt):
        """Actualiza la lógica de la pantalla."""
        pass

    def dibujar(self):
        """Dibuja todos los elementos de la pantalla."""
        pass


"""Definicion de la pantalla de login"""

class PantallaLogin(Pantalla):
    """
    Pantalla inicial del juego. Permite crear un perfil nuevo o cargar uno existente ingresando el nombre del jugador.
    """

    def __init__(self, surface):
        super().__init__(surface)
        cx = ANCHO // 2
        self.campo    = CampoTexto(cx - 180, 320, 360, 46, "Tu nombre...", max_chars=20)
        self.btn_nuevo = Boton(cx - 180, 390, 170, 44, "Nuevo jugador", color_base=(30, 60, 40), color_hover=(40, 90, 55), color_texto=VERDE_ACC)
        self.btn_cargar = Boton(cx + 10, 390, 170, 44, "Cargar perfil", color_base=(30, 40, 70), color_hover=(40, 55, 100), color_texto=AZUL_ACC)
        self.btn_ranking = Boton(cx - 80, 454, 160, 36, "Ver Ranking", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=DORADO)
        self.mensaje  = ""
        self.color_msg = ROJO_ACC
        self._jugador_resultado = None

    def manejar_eventos(self, eventos):
        for ev in eventos:
            self.campo.manejar_evento(ev)
            if self.btn_nuevo.fue_clickeado(ev):
                self._accion_nuevo()
            if self.btn_cargar.fue_clickeado(ev):
                self._accion_cargar()
            if self.btn_ranking.fue_clickeado(ev):
                self.siguiente = "ranking"
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                if self.campo.activo:
                    self._accion_nuevo()

    def _accion_nuevo(self):
        """Crea un nuevo jugador o informa si ya existe."""
        nombre = self.campo.texto.strip()
        if not nombre:
            self.mensaje = "Ingresá un nombre para continuar."
            self.color_msg = ROJO_ACC
            return
        if jugador_existe(nombre):
            self.mensaje = f"'{nombre}' ya existe. Cargando perfil..."
            self.color_msg = DORADO
            self._jugador_resultado = leer_jugador(nombre)
            self.siguiente = "menu"
            return
        jugador = Jugador(nombre)
        crear_jugador(jugador)
        self._jugador_resultado = jugador
        self.mensaje = f"¡Bienvenido, {nombre}!"
        self.color_msg = VERDE_ACC
        self.siguiente = "menu"

    def _accion_cargar(self):
        """Carga el perfil de un jugador existente."""
        nombre = self.campo.texto.strip()
        if not nombre:
            self.mensaje = "Ingresá tu nombre para cargar el perfil."
            self.color_msg = ROJO_ACC
            return
        jugador = leer_jugador(nombre)
        if not jugador:
            self.mensaje = f"No se encontró el jugador '{nombre}'."
            self.color_msg = ROJO_ACC
            return
        self._jugador_resultado = jugador
        self.siguiente = "menu"

    def actualizar(self, dt):
        pos = pygame.mouse.get_pos()
        self.campo.actualizar(dt)
        self.btn_nuevo.actualizar(pos)
        self.btn_cargar.actualizar(pos)
        self.btn_ranking.actualizar(pos)

    def dibujar(self):
        dibujar_fondo(self.surface)

        # Logo / título principal
        dibujar_texto(self.surface, "MUSEUM", FUENTES["titulo"], DORADO, ANCHO // 2, 120, centrado=True)
        dibujar_texto(self.surface, "CARD COLLECTOR", FUENTES["subtitulo"], DORADO_CLARO, ANCHO // 2, 178, centrado=True)
        dibujar_linea_dorada(self.surface, 200, 218, ANCHO - 200, 218, 2)
        dibujar_linea_dorada(self.surface, 250, 222, ANCHO - 250, 222, 1)
        dibujar_texto(self.surface, "Programación 3  —  2026 — Un proyecto de Felix Doura", FUENTES["pequeña"], GRIS_CLARO, ANCHO // 2, 234, centrado=True)

        # Decoración: columnas laterales
        for x in (80, ANCHO - 80):
            pygame.draw.rect(self.surface, DORADO_OSC, (x - 1, 100, 2, 420))

        # Panel central
        panel = pygame.Rect(ANCHO // 2 - 220, 280, 440, 240)
        dibujar_rect_redondeado(self.surface, FONDO_PANEL, panel, radio=12, borde=1, color_borde=DORADO_OSC)
        dibujar_texto(self.surface, "Ingresá tu nombre", FUENTES["h2"], DORADO, ANCHO // 2, 294, centrado=True)

        self.campo.dibujar(self.surface)
        self.btn_nuevo.dibujar(self.surface)
        self.btn_cargar.dibujar(self.surface)
        self.btn_ranking.dibujar(self.surface)

        if self.mensaje:
            dibujar_texto(self.surface, self.mensaje, FUENTES["pequeña"], self.color_msg, ANCHO // 2, 500, centrado=True)

        dibujar_texto(self.surface, "Coleccioná las 12 cartas de museos del mundo", FUENTES["pequeña"], GRIS_CLARO, ANCHO // 2, 560, centrado=True)
        dibujar_texto(self.surface, "Respondé preguntas de cultura general para desbloquearlas", FUENTES["pequeña"], GRIS_OSC, ANCHO // 2, 580, centrado=True)


"""Pantalla de menu principal"""

class PantallaMenu(Pantalla):
    """
    Menú principal del juego. Muestra el progreso del jugador y da acceso a las distintas secciones.
    """

    def __init__(self, surface, jugador: Jugador):
        super().__init__(surface)
        self.jugador = jugador
        self.gestor  = GestorJuego(jugador)

        cx = ANCHO // 2
        y0 = 280
        sep = 64
        self.botones = [
            Boton(cx - 200, y0,         400, 50, "Jugar", color_base=(30, 50, 80), color_hover=(45, 75, 120), color_texto=AZUL_ACC),
            Boton(cx - 200, y0 + sep,   400, 50, "Mi Colección", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=BLANCO),
            Boton(cx - 200, y0 + sep*2, 400, 50, "Ranking", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=BLANCO),
            Boton(cx - 200, y0 + sep*3, 400, 50, "Eliminar perfil", color_base=(40, 22, 22), color_hover=(70, 30, 30), color_texto=ROJO_ACC),
            Boton(cx - 200, y0 + sep*4, 400, 50, "Salir", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=GRIS_CLARO),
        ]
        self.acciones = ["cartas", "coleccion", "ranking", "confirmar_eliminar", "salir"]
        self._confirmar_eliminar = False

    def manejar_eventos(self, eventos):
        for ev in eventos:
            for i, btn in enumerate(self.botones):
                if btn.fue_clickeado(ev):
                    accion = self.acciones[i]
                    if accion == "confirmar_eliminar":
                        self._confirmar_eliminar = not self._confirmar_eliminar
                    else:
                        self.siguiente = accion
            if self._confirmar_eliminar and ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_s:
                    eliminar_jugador(self.jugador.nombre)
                    self.siguiente = "login"
                elif ev.key == pygame.K_n:
                    self._confirmar_eliminar = False

    def actualizar(self, dt):
        pos = pygame.mouse.get_pos()
        for btn in self.botones:
            btn.actualizar(pos)

    def dibujar(self):
        dibujar_fondo(self.surface)
        dibujar_encabezado(self.surface, "MUSEUM CARD COLLECTOR")

        # Tarjeta de perfil
        progreso = self.gestor.get_progreso()
        panel = pygame.Rect(60, 90, ANCHO - 120, 130)
        dibujar_rect_redondeado(self.surface, FONDO_PANEL, panel, radio=10, borde=1, color_borde=DORADO_OSC)

        dibujar_texto(self.surface, f"{self.jugador.nombre}", FUENTES["h2"], DORADO, 90, 108)
        dibujar_texto(self.surface, f"Partidas jugadas: {self.jugador.partidas_jugadas}  |  " f"Registrado: {self.jugador.fecha_registro[:10]}", FUENTES["pequeña"], GRIS_CLARO, 90, 138)

        # Barra de progreso
        dibujar_texto(self.surface, f"Colección: {progreso['cartas_desbloqueadas']} / {progreso['total_cartas']} cartas", FUENTES["cuerpo"], BLANCO, 90, 162)
        barra_fondo = pygame.Rect(90, 186, 560, 14)
        dibujar_rect_redondeado(self.surface, GRIS_OSC, barra_fondo, radio=7)
        if progreso["porcentaje"] > 0:
            barra_llena = pygame.Rect(90, 186, int(560 * progreso["porcentaje"] / 100), 14)
            dibujar_rect_redondeado(self.surface, DORADO, barra_llena, radio=7)
        dibujar_texto(self.surface, f"{progreso['porcentaje']}%", FUENTES["pequeña"], DORADO, 660, 186)

        # Puntaje grande
        dibujar_texto(self.surface, str(self.jugador.puntaje), FUENTES["grande"], DORADO, ANCHO - 160, 100, centrado=True)
        dibujar_texto(self.surface, "PUNTOS", FUENTES["pequeña"], DORADO_OSC, ANCHO - 160, 175, centrado=True)

        for btn in self.botones:
            btn.dibujar(self.surface)

        if self._confirmar_eliminar:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.surface.blit(overlay, (0, 0))
            dialogo = pygame.Rect(ANCHO // 2 - 240, ALTO // 2 - 80, 480, 160)
            dibujar_rect_redondeado(self.surface, FONDO_PANEL, dialogo, radio=12, borde=2, color_borde=ROJO_ACC)
            dibujar_texto(self.surface, "¿Eliminar perfil?", FUENTES["h2"], ROJO_ACC, ANCHO // 2, ALTO // 2 - 60, centrado=True)
            dibujar_texto(self.surface, f"Se borrará el perfil de '{self.jugador.nombre}' permanentemente.", FUENTES["pequeña"], GRIS_CLARO, ANCHO // 2, ALTO // 2 - 28, centrado=True)
            dibujar_texto(self.surface, "Presioná  S  para confirmar  |  N  para cancelar", FUENTES["cuerpo_b"], DORADO, ANCHO // 2, ALTO // 2 + 10, centrado=True)


"""Selección de las cartas"""

class PantallaCartas(Pantalla):
    """
    Muestra la grilla de cartas disponibles para desbloquear. El jugador selecciona una carta para iniciar una ronda de preguntas.
    """
    def __init__(self, surface, jugador: Jugador, gestor: GestorJuego):
        super().__init__(surface)
        self.jugador   = jugador
        self.gestor    = gestor
        self.disponibles = gestor.get_cartas_disponibles()
        self.carta_sel = None

        self.btn_volver = Boton(30, 30, 110, 36, "Volver", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=GRIS_CLARO)
        self.btn_jugar  = Boton(ANCHO // 2 - 100, 630, 200, 44, "¡Jugar esta carta!", color_base=(30, 60, 40), color_hover=(45, 90, 60), color_texto=VERDE_ACC)
        self.btn_jugar.activo = False
        self.scroll = 0
        self._extracto_wiki = ""
        self._construir_grilla()

    def _construir_grilla(self):
        """Construye los rectangulos de la grilla de cartas. Estuve buscando si había alguna mejor forma de armar esta grilla, pero con un for y despues usar las variables
        de x y armando los margenes quedaba de la forma mas elegande posible."""
        self.rects_cartas = []
        cols, ancho_c, alto_c = 4, 200, 110
        margen_x, margen_y   = 40, 100
        gap_x, gap_y         = 15, 15
        for i, carta in enumerate(self.disponibles):
            col = i % cols
            fila = i // cols
            x = margen_x + col * (ancho_c + gap_x)
            y = margen_y + fila * (alto_c + gap_y)
            self.rects_cartas.append(pygame.Rect(x, y, ancho_c, alto_c))

    def manejar_eventos(self, eventos):
        for ev in eventos:
            if self.btn_volver.fue_clickeado(ev):
                self.siguiente = "menu"
            if self.btn_jugar.fue_clickeado(ev) and self.carta_sel:
                self.siguiente = "ronda"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, rect in enumerate(self.rects_cartas):
                    r_scroll = rect.move(0, self.scroll)
                    if r_scroll.collidepoint(ev.pos):
                        nueva = self.disponibles[i]
                        if nueva != self.carta_sel:
                            self.carta_sel = nueva
                            self.btn_jugar.activo = True
                            self._extracto_wiki = obtener_extracto(nueva.museo)

    def actualizar(self, dt):
        pos = pygame.mouse.get_pos()
        self.btn_volver.actualizar(pos)
        self.btn_jugar.actualizar(pos)

    def dibujar(self):
        dibujar_fondo(self.surface)
        dibujar_encabezado(self.surface, "SELECCIONAR CARTA", "Elegí un museo para intentar desbloquear su carta")

        if not self.disponibles:
            dibujar_texto(self.surface, "🎊 ¡Desbloqueaste todas las cartas!", FUENTES["subtitulo"], DORADO, ANCHO // 2, 300, centrado=True)
        else:
            for i, (carta, rect) in enumerate(zip(self.disponibles, self.rects_cartas)):
                r = rect.move(0, self.scroll)
                es_sel = (carta == self.carta_sel)
                es_esp = (carta.dificultad == "especial")

                color_f = (35, 28, 55) if es_esp else FONDO_CARTA
                color_b = ESPECIAL if es_esp else (DORADO if es_sel else DORADO_OSC)
                grosor  = 2 if es_sel else 1

                dibujar_rect_redondeado(self.surface, color_f, r, radio=10, borde=grosor, color_borde=color_b)

                # Ícono según dificultad
                icono = "★" if es_esp else "·"
                color_icono = ESPECIAL if es_esp else DORADO_OSC
                dibujar_texto(self.surface, icono, FUENTES["h2"], color_icono, r.x + 10, r.y + 8)

                # Nombre y datos
                dibujar_texto(self.surface, carta.nombre, FUENTES["cuerpo_b"], DORADO if es_sel else BLANCO, r.x + 10, r.y + 36, max_ancho=r.width - 15)
                dibujar_texto(self.surface, carta.pais, FUENTES["pequeña"], GRIS_CLARO, r.x + 10, r.y + 60)
                preguntas = carta.get_preguntas_requeridas()
                dibujar_texto(self.surface, f"{preguntas} preguntas", FUENTES["pequeña"], ESPECIAL if es_esp else AZUL_ACC, r.x + 10, r.y + 80)

        self.btn_volver.dibujar(self.surface)
        if self.carta_sel:
            # Panel inferior con info de Wikipedia del museo seleccionado
            panel_info = pygame.Rect(30, 548, ANCHO - 60, 82)
            dibujar_rect_redondeado(self.surface, FONDO_PANEL, panel_info, radio=8, borde=1, color_borde=DORADO_OSC)
            dibujar_texto(self.surface, f"{self.carta_sel.nombre}  —  {self.carta_sel.museo}", FUENTES["cuerpo_b"], DORADO, 46, 556)
            extracto = self._extracto_wiki or "Cargando información..."
            palabras = extracto.split()
            linea, lineas = "", []
            for p in palabras:
                prueba = linea + " " + p if linea else p
                if FUENTES["pequeña"].size(prueba)[0] < ANCHO - 100:
                    linea = prueba
                else:
                    lineas.append(linea)
                    linea = p
                    if len(lineas) == 2:
                        break
            if linea and len(lineas) < 2:
                lineas.append(linea)
            y_w = 576
            for ln in lineas[:2]:
                dibujar_texto(self.surface, ln, FUENTES["pequeña"], GRIS_CLARO, 46, y_w)
                y_w += 17
            self.btn_jugar.dibujar(self.surface)


"""Pantalla de ronda actual"""

class PantallaRonda(Pantalla):
    """
    Pantalla de juego activo. Presenta cada pregunta con sus opciones y gestiona la evaluación de respuestas.
    """

    def __init__(self, surface, jugador: Jugador, gestor: GestorJuego, carta):
        super().__init__(surface)
        self.jugador    = jugador
        self.gestor     = gestor
        self.carta      = carta
        self.pregunta_actual = None
        self.num_pregunta    = 0
        self.total_preguntas = carta.get_preguntas_requeridas()
        self.feedback        = ""
        self.color_feedback  = BLANCO
        self.respondida      = False
        self.botones_opciones = []
        self.btn_siguiente    = Boton(ANCHO // 2 - 100, 600, 200, 44, "Siguiente", color_base=(30, 50, 80), color_hover=(45, 75, 110), color_texto=AZUL_ACC)
        self.btn_siguiente.activo = False
        self.resultado = None

        gestor.iniciar_ronda(carta)
        self._avanzar_pregunta()

    def _avanzar_pregunta(self):
        """Carga la siguiente pregunta de la cola y construye sus botones."""
        self.pregunta_actual = self.gestor.get_siguiente_pregunta()
        self.num_pregunta += 1
        self.feedback   = ""
        self.respondida = False
        self.btn_siguiente.activo = False
        self._construir_botones()

    def _construir_botones(self):
        """Construye los botones de opciones para la pregunta actual."""
        self.botones_opciones = []
        opciones = self.pregunta_actual["opciones"]
        y_inicio = 380
        for i, op in enumerate(opciones):
            btn = Boton(ANCHO // 2 - 280, y_inicio + i * 54, 560, 46, op, color_base=FONDO_CARTA, color_hover=(40, 50, 80), color_texto=BLANCO)
            self.botones_opciones.append(btn)

    def manejar_eventos(self, eventos):
        for ev in eventos:
            if self.btn_siguiente.fue_clickeado(ev):
                self._siguiente()
            for i, btn in enumerate(self.botones_opciones):
                if btn.fue_clickeado(ev) and not self.respondida:
                    self._responder(i)

    def _responder(self, indice):
        """Procesa la respuesta seleccionada por el jugador."""
        self.respondida = True
        respuesta = self.pregunta_actual["opciones"][indice]
        correcto  = self.gestor.responder(self.pregunta_actual, respuesta)

        # Colorear botones según correcto/incorrecto
        for i, btn in enumerate(self.botones_opciones):
            if btn.texto == self.pregunta_actual["respuesta"]:
                btn.color_base = (25, 60, 35)
                btn.color_texto = VERDE_ACC
            elif i == indice and not correcto:
                btn.color_base = (60, 25, 25)
                btn.color_texto = ROJO_ACC
            btn.activo = False

        if correcto:
            self.feedback = "¡Correcto!  +10 puntos"
            self.color_feedback = VERDE_ACC
        else:
            self.feedback = f"Incorrecto. Era: {self.pregunta_actual['respuesta']}"
            self.color_feedback = ROJO_ACC

        self.btn_siguiente.activo = True

    def _siguiente(self):
        """Avanza a la siguiente pregunta o cierra la ronda."""
        if not self.respondida:
            return
        if self.gestor.hay_siguiente_pregunta():
            self._avanzar_pregunta()
        else:
            self.resultado = self.gestor.finalizar_ronda()
            self.siguiente = "resultado"

    def actualizar(self, dt):
        pos = pygame.mouse.get_pos()
        self.btn_siguiente.actualizar(pos)
        for btn in self.botones_opciones:
            btn.actualizar(pos)

    def dibujar(self):
        if not self.pregunta_actual:
            return
        dibujar_fondo(self.surface)

        # Encabezado con info de la carta
        dibujar_encabezado(self.surface, f"{self.carta.museo}", f"{self.carta.pais}  —  Pregunta {self.num_pregunta} / {self.total_preguntas}")

        # Barra de progreso de la ronda
        barra = pygame.Rect(60, 88, ANCHO - 120, 8)
        dibujar_rect_redondeado(self.surface, GRIS_OSC, barra, radio=4)
        progreso = int((self.num_pregunta / self.total_preguntas) * (ANCHO - 120))
        if progreso > 0:
            dibujar_rect_redondeado(self.surface, ESPECIAL if self.carta.dificultad == "especial" else DORADO, pygame.Rect(60, 88, progreso, 8), radio=4)

        # Panel de pregunta
        panel = pygame.Rect(60, 110, ANCHO - 120, 240)
        dibujar_rect_redondeado(self.surface, FONDO_PANEL, panel, radio=10, borde=1, color_borde=DORADO_OSC)

        # Texto de la pregunta
        palabras = self.pregunta_actual["pregunta"].split()
        linea, lineas = "", []
        for p in palabras:
            prueba = linea + " " + p if linea else p
            if FUENTES["h2"].size(prueba)[0] < ANCHO - 160:
                linea = prueba
            else:
                lineas.append(linea)
                linea = p
        lineas.append(linea)

        y_preg = 140
        for linea in lineas:
            dibujar_texto(self.surface, linea, FUENTES["h2"], BLANCO, ANCHO // 2, y_preg, centrado=True)
            y_preg += 34

        # Puntaje actual
        dibujar_texto(self.surface, f"{self.jugador.puntaje} pts", FUENTES["cuerpo"], DORADO, ANCHO - 160, 120)

        # Botones de opciones
        for btn in self.botones_opciones:
            btn.dibujar(self.surface)

        # Feedback
        if self.feedback:
            dibujar_texto(self.surface, self.feedback, FUENTES["cuerpo_b"], self.color_feedback, ANCHO // 2, 568, centrado=True)

        self.btn_siguiente.dibujar(self.surface)


"""Pantalla del resultado"""

class PantallaResultado(Pantalla):
    """
    Muestra el resultado al finalizar una ronda: si se desbloqueó
    la carta, los aciertos obtenidos y el dato curioso en caso de
    que sea una carta especial.
    """

    def __init__(self, surface, resultado: dict, jugador: Jugador):
        super().__init__(surface)
        self.resultado = resultado
        self.jugador   = jugador
        cx = ANCHO // 2

        self.btn_seguir = Boton(cx - 110, 580, 220, 48, "Seguir jugando", color_base=(30, 50, 80), color_hover=(45, 75, 110), color_texto=AZUL_ACC)
        self.btn_menu   = Boton(cx - 110, 638, 220, 38, "Menú principal", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=GRIS_CLARO)

    def manejar_eventos(self, eventos):
        for ev in eventos:
            if self.btn_seguir.fue_clickeado(ev):
                self.siguiente = "cartas"
            if self.btn_menu.fue_clickeado(ev):
                self.siguiente = "menu"

    def actualizar(self, dt):
        pos = pygame.mouse.get_pos()
        self.btn_seguir.actualizar(pos)
        self.btn_menu.actualizar(pos)

    def dibujar(self):
        dibujar_fondo(self.surface)
        desbloqueada = self.resultado["carta_desbloqueada"]
        carta        = self.resultado["carta"]
        aciertos     = self.resultado["aciertos"]
        requeridos   = self.resultado["requeridos"]

        # Guardia: si la carta es None no hay nada que mostrar
        if carta is None:
            dibujar_texto(self.surface, "Error al cargar el resultado.", FUENTES["cuerpo"], ROJO_ACC, ANCHO // 2, 300, centrado=True)
            self.btn_menu.dibujar(self.surface)
            return

        if desbloqueada:
            dibujar_texto(self.surface, "¡CARTA DESBLOQUEADA!", FUENTES["subtitulo"], DORADO, ANCHO // 2, 80, centrado=True)
            dibujar_linea_dorada(self.surface, 100, 118, ANCHO - 100, 118, 2)
        else:
            dibujar_texto(self.surface, "RONDA TERMINADA", FUENTES["subtitulo"], GRIS_CLARO, ANCHO // 2, 80, centrado=True)
            dibujar_linea_dorada(self.surface, 100, 118, ANCHO - 100, 118, 1)

        # Panel de carta
        panel = pygame.Rect(ANCHO // 2 - 260, 140, 520, 200)
        color_borde = DORADO if desbloqueada else GRIS_OSC
        dibujar_rect_redondeado(self.surface, FONDO_PANEL, panel, radio=12, borde=2, color_borde=color_borde)

        es_esp = carta.dificultad == "especial"
        dibujar_texto(self.surface, "CARTA ESPECIAL" if es_esp else "CARTA NORMAL", FUENTES["pequeña"], ESPECIAL if es_esp else DORADO_OSC, ANCHO // 2, 158, centrado=True)
        dibujar_texto(self.surface, carta.nombre, FUENTES["subtitulo"], DORADO if desbloqueada else GRIS_CLARO, ANCHO // 2, 182, centrado=True)
        dibujar_texto(self.surface, carta.museo, FUENTES["cuerpo"], BLANCO, ANCHO // 2, 218, centrado=True)
        dibujar_texto(self.surface, carta.pais, FUENTES["cuerpo"], GRIS_CLARO, ANCHO // 2, 244, centrado=True)

        # Dato curioso para especiales
        if es_esp and hasattr(carta, "dato_curioso") and carta.dato_curioso:
            palabras = carta.dato_curioso.split()
            linea, lineas = "", []
            for p in palabras:
                prueba = linea + " " + p if linea else p
                if FUENTES["pequeña"].size(prueba)[0] < 480:
                    linea = prueba
                else:
                    lineas.append(linea)
                    linea = p
            lineas.append(linea)
            y_dato = 272
            for l in lineas[:2]:
                dibujar_texto(self.surface, l, FUENTES["pequeña"], ESPECIAL, ANCHO // 2, y_dato, centrado=True)
                y_dato += 20

        # Resultado de aciertos
        color_res = VERDE_ACC if desbloqueada else ROJO_ACC
        dibujar_texto(self.surface, f"Aciertos: {aciertos} / {requeridos}", FUENTES["h2"], color_res, ANCHO // 2, 362, centrado=True)

        if desbloqueada:
            bonus = 100 if es_esp else 50
            dibujar_texto(self.surface, f"+{bonus} puntos de bonus", FUENTES["cuerpo"], DORADO, ANCHO // 2, 400, centrado=True)
        else:
            dibujar_texto(self.surface, "¡Intentalo de nuevo!", FUENTES["cuerpo"], GRIS_CLARO, ANCHO // 2, 400, centrado=True)

        dibujar_texto(self.surface, f"Puntaje total: {self.jugador.puntaje}", FUENTES["cuerpo_b"], DORADO, ANCHO // 2, 440, centrado=True)

        self.btn_seguir.dibujar(self.surface)
        self.btn_menu.dibujar(self.surface)


"""Pantalla de coleccion"""

class PantallaColeccion(Pantalla):
    """
    Muestra todas las cartas desbloqueadas por el jugador en una grilla.
    """

    def __init__(self, surface, jugador: Jugador, gestor: GestorJuego):
        super().__init__(surface)
        self.jugador      = jugador
        self.gestor       = gestor
        self.desbloqueadas = gestor.get_cartas_desbloqueadas()
        self.btn_volver   = Boton(30, 30, 110, 36, "Volver", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=GRIS_CLARO)

    def manejar_eventos(self, eventos):
        for ev in eventos:
            if self.btn_volver.fue_clickeado(ev):
                self.siguiente = "menu"

    def actualizar(self, dt):
        self.btn_volver.actualizar(pygame.mouse.get_pos())

    def dibujar(self):
        dibujar_fondo(self.surface)
        dibujar_encabezado(self.surface, "MI COLECCIÓN", f"{len(self.desbloqueadas)} de 12 cartas desbloqueadas")

        if not self.desbloqueadas:
            dibujar_texto(self.surface, "Todavía no tenés ninguna carta. ¡Jugá para conseguirlas!", FUENTES["cuerpo"], GRIS_CLARO, ANCHO // 2, 350, centrado=True)
        else:
            cols, ancho_c, alto_c = 4, 210, 100
            gap_x, gap_y, margen_x, margen_y = 14, 14, 35, 100
            for i, carta in enumerate(self.desbloqueadas):
                col  = i % cols
                fila = i // cols
                x = margen_x + col * (ancho_c + gap_x)
                y = margen_y + fila * (alto_c + gap_y)
                rect = pygame.Rect(x, y, ancho_c, alto_c)
                es_esp = carta.dificultad == "especial"
                color_f = (35, 28, 55) if es_esp else FONDO_CARTA
                color_b = ESPECIAL if es_esp else DORADO
                dibujar_rect_redondeado(self.surface, color_f, rect, radio=10, borde=1, color_borde=color_b)
                dibujar_texto(self.surface, "!!!" if es_esp else "·", FUENTES["h2"], ESPECIAL if es_esp else DORADO_OSC, x + 8, y + 6)
                dibujar_texto(self.surface, carta.nombre, FUENTES["cuerpo_b"], DORADO, x + 8, y + 34, max_ancho=ancho_c - 12)
                dibujar_texto(self.surface, carta.pais, FUENTES["pequeña"], GRIS_CLARO, x + 8, y + 58)
                dibujar_texto(self.surface, carta.museo, FUENTES["pequeña"], GRIS_OSC, x + 8, y + 76, max_ancho=ancho_c - 12)

        self.btn_volver.dibujar(self.surface)


"""Pantalla del ranking"""

class PantallaRanking(Pantalla):
    """
    Muestra el ranking global de jugadores ordenado por puntaje descendente.
    """
    def __init__(self, surface):
        super().__init__(surface)
        self.jugadores  = leer_ranking()
        self.btn_volver = Boton(30, 30, 110, 36, "Volver", color_base=FONDO_PANEL, color_hover=GRIS_OSC, color_texto=GRIS_CLARO)

    def manejar_eventos(self, eventos):
        for ev in eventos:
            if self.btn_volver.fue_clickeado(ev):
                self.siguiente = "login"

    def actualizar(self, dt):
        self.btn_volver.actualizar(pygame.mouse.get_pos())

    def dibujar(self):
        dibujar_fondo(self.surface)
        dibujar_encabezado(self.surface, "RANKING GLOBAL", "Jugadores con más puntos")

        medallas = ["1.", "2.", "3."]
        y0 = 100
        panel_w = ANCHO - 120

        if not self.jugadores:
            dibujar_texto(self.surface, "Aún no hay jugadores registrados.", FUENTES["cuerpo"], GRIS_CLARO, ANCHO // 2, 300, centrado=True)
        else:
            for i, j in enumerate(self.jugadores[:10]):
                y = y0 + i * 52
                rect = pygame.Rect(60, y, panel_w, 44)
                color_f = (35, 30, 10) if i == 0 else FONDO_PANEL
                color_b = DORADO if i == 0 else DORADO_OSC
                dibujar_rect_redondeado(self.surface, color_f, rect, radio=8, borde=1, color_borde=color_b)

                medalla = medallas[i] if i < 3 else f"{i+1}."
                dibujar_texto(self.surface, medalla, FUENTES["cuerpo_b"], DORADO if i == 0 else GRIS_CLARO, 76, y + 12)
                dibujar_texto(self.surface, j.nombre, FUENTES["cuerpo_b"], DORADO if i == 0 else BLANCO, 120, y + 12)
                dibujar_texto(self.surface, f"{j.puntaje} pts", FUENTES["cuerpo_b"], DORADO if i == 0 else AZUL_ACC, ANCHO - 200, y + 12)
                dibujar_texto(self.surface, f"{j.total_cartas()} cartas", FUENTES["pequeña"], GRIS_CLARO, ANCHO - 320, y + 14)

        self.btn_volver.dibujar(self.surface)


"""Controlador principal"""

class Interfaz:
    """
    Controlador principal de la interfaz gráfica.
    Orquesta el ciclo de juego y la transición entre pantallas.

    Los atributos son la pantalla principal, el reloj, el jugador que esta activo, el gestor y la pantalla que esta renderizandose actualemente"
    """

    def __init__(self):
        """Inicializa la ventana de Pygame y carga la pantalla de login."""
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.clock  = pygame.time.Clock()
        self.jugador = None
        self.gestor  = None
        self.carta_activa = None
        self.resultado_ronda = None
        self.pantalla_actual = PantallaLogin(self.screen)

    def _transicionar(self, destino: str):
        """
        Crea e instancia la pantalla correspondiente al destino indicado.
        """
        if destino == "login":
            self.jugador = None
            self.gestor  = None
            self.pantalla_actual = PantallaLogin(self.screen)

        elif destino == "menu":
            if hasattr(self.pantalla_actual, "_jugador_resultado") and \
               self.pantalla_actual._jugador_resultado:
               self.jugador = self.pantalla_actual._jugador_resultado
            self.gestor = GestorJuego(self.jugador)
            self.pantalla_actual = PantallaMenu(self.screen, self.jugador)

        elif destino == "cartas":
            self.gestor = GestorJuego(self.jugador)
            self.pantalla_actual = PantallaCartas(self.screen, self.jugador, self.gestor)

        elif destino == "ronda":
            self.carta_activa = self.pantalla_actual.carta_sel
            self.pantalla_actual = PantallaRonda(self.screen, self.jugador, self.gestor, self.carta_activa)

        elif destino == "resultado":
            self.resultado_ronda = getattr(self.pantalla_actual, "resultado", None)
            # Si el resultado o la carta son None, volver al menú silenciosamente
            if not self.resultado_ronda or self.resultado_ronda.get("carta") is None:
                self.pantalla_actual = PantallaMenu(self.screen, self.jugador)
                return
            self.pantalla_actual = PantallaResultado(
                self.screen, self.resultado_ronda, self.jugador)

        elif destino == "coleccion":
            self.pantalla_actual = PantallaColeccion(self.screen, self.jugador, self.gestor)

        elif destino == "ranking":
            self.pantalla_actual = PantallaRanking(self.screen)

        elif destino == "salir":
            pygame.quit()
            sys.exit()

    def ejecutar(self):
        """
        Bucle principal del juego. Gestiona eventos, actualiza la lógica
        y dibuja la pantalla activa a los FPS configurados.
        """
        while True:
            dt = self.clock.tick(FPS)
            eventos = pygame.event.get()

            for ev in eventos:
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.pantalla_actual.manejar_eventos(eventos)
            self.pantalla_actual.actualizar(dt)
            self.pantalla_actual.dibujar()

            # Transición de pantalla
            if self.pantalla_actual.siguiente:
                self._transicionar(self.pantalla_actual.siguiente)

            pygame.display.flip()
