"""
main.py
-------
Punto de entrada del juego Museum Card Collector.
Ejecutar con: python main.py

En caso que sea la primera vez que se juega, no olvidar que hay que instalar las dependencias!!
    pip install -r requirements.txt
"""

from gui.interfaz import Interfaz


def main():
    """
    Función principal. Inicializa y lanza la interfaz gráfica del juego.
    """
    juego = Interfaz()
    juego.ejecutar()


if __name__ == "__main__":
    main()