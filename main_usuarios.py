'''
main_usuarios.py - Pipeline de la tabla `usuarios`: HU USR-F01 + X01, L01, Q01 y G01.

Cada tabla del equipo tiene su propio main (main_registros.py, main_usuarios.py, ...).
Este solo ejecuta los archivos de `usuarios`.

Ejecutar desde la raíz del proyecto, con el .venv activado:
    python main_usuarios.py              todo el pipeline (fases 1 a 4)
    python main_usuarios.py --fase 2     solo una fase (1, 2, 3 o 4)

Fases (cada una usa lo que generó la anterior):
  1. Simula y exporta 400 filas         -> data/crudo/usuarios_sucio.csv / .xlsx / .json
  2. Limpia el CSV sucio                -> data/limpio/usuarios_limpio.csv
  3. Hace las 5 consultas               -> data/limpio/usuarios_consulta_1..5.csv
  4. Genera 3 gráficas y conclusiones   -> reportes/usuarios_grafica_1..3.png

Los archivos generados se reemplazan en cada ejecución (mismo nombre); no se acumulan.
'''

import argparse
import os
import sys
from pathlib import Path

#1. Trabajar siempre desde la raíz del proyecto (las rutas de la HU son relativas a ella)
RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
for carpeta in ("exportacion", "limpieza", "consultas", "graficas"):
    sys.path.insert(0, str(RAIZ / "src" / "notebook" / carpeta))

from exportacion_usuario import exportar_usuarios
from limpieza_usuario import limpiar_usuarios, RUTA_SUCIO, RUTA_LIMPIO
from consulta_usuario import consultar_usuarios
from reporte_usuario import generar_reporte_usuarios


#2. Comprobar que existe lo que necesita una fase (si se ejecuta sola)
def necesita(ruta, fase_anterior):
    if not Path(ruta).is_file():
        print(f"Falta {ruta}. Ejecuta antes la fase {fase_anterior}: python main_usuarios.py --fase {fase_anterior}")
        sys.exit(1)


#3. Las cuatro fases
def fase_1():
    print("1) Simulando y exportando usuarios (USR-F01 + X01)...")
    exportar_usuarios()


def fase_2():
    necesita(RUTA_SUCIO, 1)
    print("\n2) Limpiando usuarios (USR-L01)...\n")
    limpiar_usuarios()


def fase_3():
    necesita(RUTA_LIMPIO, 2)
    print("\n3) Haciendo las consultas (USR-Q01)...\n")
    consultar_usuarios()


def fase_4():
    necesita(RUTA_LIMPIO, 2)
    print("\n4) Generando las gráficas y conclusiones (USR-G01)...\n")
    generar_reporte_usuarios()


FASES = {1: fase_1, 2: fase_2, 3: fase_3, 4: fase_4}


def main():
    analizador = argparse.ArgumentParser(description="Pipeline de la tabla usuarios (USR-F01 + X01, L01, Q01, G01).")
    analizador.add_argument("--fase", type=int, choices=FASES, help="ejecuta solo esa fase (1, 2, 3 o 4)")
    args = analizador.parse_args()
    for numero in ([args.fase] if args.fase else FASES):
        FASES[numero]()


if __name__ == "__main__":
    main()
