# Museum Card Collector

Juego de colección de cartas de museos famosos del mundo, desarrollado en Python con interfaz gráfica en Pygame.  
Proyecto para el trabajo final | Felix Doura — **Programación 3** | Facultad de Ingeniería Informática | 2026

---

## Descripción

El jugador responde preguntas de cultura general sobre países del mundo para desbloquear cartas que representan museos famosos. El objetivo es completar la colección de **12 cartas**: 10 normales y 2 especiales de mayor dificultad.

---

## Estructura del proyecto

```
museum_collector/
│
├── main.py                  # Punto de entrada del programa
│
├── models/
│   ├── __init__.py
│   ├── carta.py             # Clase abstracta Carta + CartaNormal + CartaEspecial
│   └── jugador.py           # Clase Jugador (perfil, colección, puntaje)
│
├── logic/
│   ├── __init__.py
│   ├── crud.py              # CRUD completo sobre jugadores.json
│   └── gestor_juego.py      # Lógica del juego: rondas, queue de preguntas
│
├── gui/
│   ├── __init__.py
│   └── interfaz.py          # Interfaz gráfica con Pygame
│
├── data/
│   ├── cartas.json          # Definición de las 12 cartas
│   ├── preguntas.json       # Banco de preguntas por país
│   └── jugadores.json       # Perfiles y progreso de jugadores (generado al ejecutar)
│
├── assets/                  # Imágenes, fuentes y recursos gráficos
│
├── requirements.txt         # Dependencias externas
└── .gitignore
```

---

## Requisitos

- Python **3.10** o superior

---

## Instalación y ejecución (Windows)

### 1. Clonar el repositorio

Ejecutar:

```bash
git clone https://github.com/felixdoura/museum-card-collector.git
cd museum-card-collector
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
venv\Scripts\activate
```

> Revisar que venv quede activo (puede haber un problema con la barra del comando del Script, me falló un par de veces).

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala:

| Librería | Versión | Uso |
|----------|---------|-----|
| `pygame` | 2.6.1 | Interfaz gráfica |
| `requests` | 2.32.3 | Consultas a la API de Wikipedia por el tema de las respuestas |

Las siguientes librerías no requieren instalación:
`json`, `queue`, `abc`, `datetime`, `re`

### 4. Ejecutar el juego

```bash
python main.py
```

