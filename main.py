"""
main.py
-------
Punto de entrada del juego Museum Card Collector.
Ejecutar con: python main.py

Es importante que hay que instalar las dependencias externas (instalar con pip):
    pip install -r requirements.txt  --> con este comando ya todo debería funcionar bien.

Nota: Tengo agendado para la semana 3 meter la parte gráfica. Hasta entonces jugaremos en consola, como los viejos tiempos y a mi me gusta mas jaja
"""

from models.jugador import Jugador
from logic.crud import crear_jugador, leer_jugador, jugador_existe, leer_ranking, eliminar_jugador
from logic.gestor_juego import GestorJuego

"""
Para que se vea mas lindo en la consola agrego detalles que me van a ayudar, como el separador y el encabezado:
"""
def imprimir_encabezado():
    """Imprime el encabezado visual del juego."""
    print("\n" + "=" * 50)
    print("        MUSEUM CARD COLLECTOR")
    print("        Programación 3 — 2026")
    print("=" * 50)


def imprimir_separador():
    print("-" * 50)


def pedir_opcion(opciones: list[str]) -> str:
    while True:
        entrada = input(">>> ").strip()
        if entrada in opciones:
            return entrada
        print(f"Opción inválida. Elegí entre: {', '.join(opciones)}")


def pantalla_login() -> Jugador:
    """
    Muestra la pantalla de inicio y permite crear un perfil nuevo
    o cargar uno existente.
    """
    imprimir_encabezado()
    print("\n¿Qué querés hacer?")
    print("  [1] Nuevo jugador")
    print("  [2] Cargar perfil existente")
    print("  [3] Ver ranking")
    print("  [0] Salir")

    opcion = pedir_opcion(["0", "1", "2", "3"])

    if opcion == "0":
        print("\n¡Hasta la próxima!")
        exit()

    elif opcion == "1":
        print("\nIngresá tu nombre:")
        nombre = input(">>> ").strip()
        if not nombre:
            print("El nombre no puede estar vacío.")
            return pantalla_login()
        if jugador_existe(nombre):
            print(f"Ya existe un jugador llamado '{nombre}'. Cargando perfil...")
            return leer_jugador(nombre)
        jugador = Jugador(nombre)
        crear_jugador(jugador)
        print(f"\n¡Bienvenido, {nombre}! Tu perfil fue creado.")
        return jugador

    elif opcion == "2":
        print("\nIngresá tu nombre:")
        nombre = input(">>> ").strip()
        jugador = leer_jugador(nombre)
        if not jugador:
            print(f"No se encontró el jugador '{nombre}'.")
            return pantalla_login()
        print(f"\n¡Bienvenido de vuelta, {nombre}!")
        print(f"Cartas: {jugador.total_cartas()} | Puntaje: {jugador.puntaje}")
        return jugador

    elif opcion == "3":
        pantalla_ranking()
        return pantalla_login()

def pantalla_ranking():
    """Muestra el ranking de jugadores ordenado por puntaje."""
    imprimir_separador()
    print("RANKING DE JUGADORES")
    imprimir_separador()
    ranking = leer_ranking()
    if not ranking:
        print("Aún no hay jugadores registrados.")
    else:
        for i, j in enumerate(ranking, start=1):
            print(f"  {i}. {j.nombre:<20} Puntaje: {j.puntaje:<6} Cartas: {j.total_cartas()}")
    imprimir_separador()

def menu_principal(jugador: Jugador, gestor: GestorJuego) -> str:
    """
    Muestra el menú principal del juego y retorna la opción elegida.

    Args:
        jugador (Jugador): Jugador activo.
        gestor (GestorJuego): Gestor del juego activo.

    """
    progreso = gestor.get_progreso()
    imprimir_separador()
    print(f"Jugador: {jugador.nombre}  |  Puntaje: {jugador.puntaje}")
    print(f"Colección: {progreso['cartas_desbloqueadas']}/{progreso['total_cartas']} cartas ({progreso['porcentaje']}%)")
    imprimir_separador()
    print("\n¿Qué querés hacer?")
    print("  [1] Jugar (intentar desbloquear una carta)")
    print("  [2] Ver mi colección")
    print("  [3] Ver ranking")
    print("  [4] Eliminar perfil")
    print("  [0] Salir")

    return pedir_opcion(["0", "1", "2", "3", "4"])

def pantalla_seleccion_carta(gestor: GestorJuego):
    """
    Muestra las cartas disponibles y permite al jugador elegir una
    para intentar desbloquearla.
    """
    disponibles = gestor.get_cartas_disponibles()

    if not disponibles:
        print("\n¡Felicitaciones! ¡Desbloqueaste todas las cartas!")
        return

    imprimir_separador()
    print("CARTAS DISPONIBLES PARA DESBLOQUEAR")
    imprimir_separador()
    for i, carta in enumerate(disponibles, start=1):
        tipo = "★ ESPECIAL" if carta.dificultad == "especial" else "Normal"
        preguntas = carta.get_preguntas_requeridas()
        print(f"  [{i}] {carta.nombre:<25} {carta.pais:<20} ({tipo} — {preguntas} preguntas)")

    print("  [0] Volver")
    imprimir_separador()

    opciones = ["0"] + [str(i) for i in range(1, len(disponibles) + 1)]
    opcion = pedir_opcion(opciones)

    if opcion == "0":
        return

    carta_elegida = disponibles[int(opcion) - 1]
    print(f"\n{carta_elegida.get_descripcion()}")
    print(f"\n¿Listo para responder las preguntas sobre {carta_elegida.pais}? [s/n]")

    if pedir_opcion(["s", "n"]) == "n":
        return

    jugar_ronda(gestor, carta_elegida)


def jugar_ronda(gestor: GestorJuego, carta):
    """
    Ejecuta una ronda completa de preguntas para intentar desbloquear
    la carta seleccionada.
    """
    if not gestor.iniciar_ronda(carta):
        print("No hay preguntas disponibles para este país.")
        return

    requeridos = carta.get_preguntas_requeridas()
    num_pregunta = 1

    while gestor.hay_siguiente_pregunta():
        preg = gestor.get_siguiente_pregunta()
        imprimir_separador()
        print(f"Pregunta {num_pregunta}/{requeridos} — {carta.museo}")
        print(f"\n{preg['pregunta']}\n")

        for i, opcion in enumerate(preg["opciones"], start=1):
            print(f"  [{i}] {opcion}")

        opciones_validas = [str(i) for i in range(1, len(preg["opciones"]) + 1)]
        eleccion = pedir_opcion(opciones_validas)
        respuesta_usuario = preg["opciones"][int(eleccion) - 1]

        correcto = gestor.responder(preg, respuesta_usuario)

        if correcto:
            print("¡Correcto! +10 puntos")
        else:
            print(f"Incorrecto. La respuesta era: {preg['respuesta']}")

        num_pregunta += 1

    # Resultado final de la ronda
    resultado = gestor.finalizar_ronda()
    imprimir_separador()

    if resultado["carta_desbloqueada"]:
        print(f"🎉 ¡Desbloqueaste la carta '{carta.nombre}'!")
        if carta.dificultad == "especial":
            print(f"¡Carta especial! +100 puntos de bonus")
            if hasattr(carta, "dato_curioso") and carta.dato_curioso:
                print(f"💡 {carta.dato_curioso}")
        else:
            print(f"+50 puntos de bonus")
    else:
        print(f"No desbloqueaste la carta. Acertaste {resultado['aciertos']}/{resultado['requeridos']}.")
        print("¡Intentalo de nuevo!")

def pantalla_coleccion(gestor: GestorJuego):
    """
    Muestra las cartas que el jugador ya desbloqueó.
    """
    desbloqueadas = gestor.get_cartas_desbloqueadas()
    imprimir_separador()
    print("MI COLECCIÓN")
    imprimir_separador()

    if not desbloqueadas:
        print("Todavía no tenés ninguna carta. ¡Jugá para conseguirlas!")
    else:
        for carta in desbloqueadas:
            tipo = "★" if carta.dificultad == "especial" else "·"
            print(f"  {tipo} {carta.nombre:<25} — {carta.museo} ({carta.pais})")

    imprimir_separador()

def main():
    """
    Función principal. Gestiona el flujo completo del juego:
    login, menú principal y acciones del jugador.
    """
    jugador = pantalla_login()
    gestor = GestorJuego(jugador)

    while True:
        opcion = menu_principal(jugador, gestor)

        if opcion == "0":
            print(f"\n¡Hasta la próxima, {jugador.nombre}!")
            break
        elif opcion == "1":
            pantalla_seleccion_carta(gestor)
        elif opcion == "2":
            pantalla_coleccion(gestor)
        elif opcion == "3":
            pantalla_ranking()
        elif opcion == "4":
            print(f"\n¿Seguro que querés eliminar el perfil de '{jugador.nombre}'? [s/n]")
            if pedir_opcion(["s", "n"]) == "s":
                eliminar_jugador(jugador.nombre)
                print("Perfil eliminado.")
                break


if __name__ == "__main__":
    main()

