'''
main_registros.py - Pipeline de la tabla `registros`: HU F01 + X01, L01, Q01 y G01.

Cada tabla del equipo tiene su propio main (main_registros.py, main_retos.py, ...).
Este solo ejecuta los archivos de `registros`.

Ejecutar desde la raíz del proyecto, con el .venv activado:
    python main_registros.py                  todo el pipeline (fases 1 a 4)
    python main_registros.py --fase 2         solo una fase (1, 2, 3 o 4)
    python main_registros.py --completo       muestra las tablas PASA / FALLA completas
    python main_registros.py --sin-revision   no ejecuta las skills de revisión

Fases (cada una usa lo que generó la anterior):
  1. Simula y exporta 800 filas         -> data/crudo/registros_sucio.csv / .xlsx / .json
  2. Limpia el CSV sucio                -> data/limpio/registros_limpio.csv
  3. Hace las 5 consultas               -> data/limpio/registros_consulta_1..5.csv
  4. Genera 3 gráficas y conclusiones   -> reportes/registros_grafica_1..3.png

Después de cada fase la revisa con su skill, si su carpeta está en la raíz
(revisar-simulacion-registros/, limpiar-registros/, consultar-registros/, graficar-registros/).
Las skills no están en el repositorio; si faltan, la fase se ejecuta igual y solo avisa.

Los archivos generados se reemplazan en cada ejecución (mismo nombre); no se acumulan.
'''

import argparse
import os
import subprocess
import sys
from pathlib import Path

#1. Trabajar siempre desde la raíz del proyecto (las rutas de la HU son relativas a ella)
RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
for carpeta in ("exportacion", "limpieza", "consultas", "graficas"):
    sys.path.insert(0, str(RAIZ / "notebook" / carpeta))

from exportacion_registro import exportar
from limpieza_registro import limpiar_registros, RUTA_SUCIO, RUTA_LIMPIO
from consulta_registro import consultar, CARPETA_SALIDA
from reporte_registro import generar_reporte, CARPETA

#2. Scripts de las skills que revisan cada fase
REVISOR = RAIZ / "revisar-simulacion-registros" / "scripts" / "revisar_datos.py"
VERIFICADOR_LIMPIEZA = RAIZ / "limpiar-registros" / "scripts" / "verificar_limpieza.py"
VERIFICADOR_CONSULTAS = RAIZ / "consultar-registros" / "scripts" / "verificar_consultas.py"
VERIFICADOR_REPORTE = RAIZ / "graficar-registros" / "scripts" / "verificar_reporte.py"
SCRIPT_CONSULTAS = RAIZ / "notebook" / "consultas" / "consulta_registro.py"
SCRIPT_REPORTE = RAIZ / "notebook" / "graficas" / "reporte_registro.py"

#Se llenan con los argumentos en main()
COMPLETO = False
SIN_REVISION = False


#3. Mostrar de la revisión solo el título de cada tabla, los FALLA y el resultado
def mostrar_resumen(salida):
    encabezado = []
    for linea in salida.splitlines():
        if linea.startswith("###"):
            print(linea)
            encabezado = []
        elif linea.startswith(("| Comprobación", "|---")):
            encabezado.append(linea)
        elif "| FALLA |" in linea:
            for fila in encabezado:
                print(fila)
            encabezado = []
            print(linea)
        elif "Resultado" in linea:
            print(linea)


#4. Ejecutar el script de una skill, o avisar si la skill no está en la raíz
def revisar(script, argumentos):
    if SIN_REVISION:
        return
    sys.stdout.flush()
    if not script.is_file():
        carpeta = script.parents[1].name
        print(f"(No encontré {carpeta}/ en la raíz; se omite la revisión de esta fase.)")
        return
    resultado = subprocess.run([sys.executable, str(script), *map(str, argumentos)],
                               capture_output=True, text=True, encoding="utf-8")
    if COMPLETO:
        print(resultado.stdout)
    else:
        mostrar_resumen(resultado.stdout)
    if resultado.returncode != 0:
        print(resultado.stderr)


#5. Comprobar que existe lo que necesita una fase (si se ejecuta sola)
def necesita(ruta, fase_anterior):
    if not Path(ruta).is_file():
        print(f"Falta {ruta}. Ejecuta antes la fase {fase_anterior}: python main_registros.py --fase {fase_anterior}")
        sys.exit(1)


#6. Las cuatro fases
def fase_1():
    print("1) Simulando y exportando registros (F01 + X01)...")
    rutas = exportar()
    revisar(REVISOR, rutas)


def fase_2():
    necesita(RUTA_SUCIO, 1)
    print("\n2) Limpiando registros (L01)...\n")
    limpiar_registros()
    revisar(VERIFICADOR_LIMPIEZA, [RUTA_LIMPIO, RUTA_SUCIO])


def fase_3():
    necesita(RUTA_LIMPIO, 2)
    print("\n3) Haciendo las consultas (Q01)...\n")
    consultar()
    revisar(VERIFICADOR_CONSULTAS, [RUTA_LIMPIO, CARPETA_SALIDA, SCRIPT_CONSULTAS])


def fase_4():
    necesita(RUTA_LIMPIO, 2)
    print("\n4) Generando las gráficas y conclusiones (G01)...\n")
    generar_reporte()
    revisar(VERIFICADOR_REPORTE, [CARPETA, SCRIPT_REPORTE])


FASES = {1: fase_1, 2: fase_2, 3: fase_3, 4: fase_4}


def main():
    global COMPLETO, SIN_REVISION
    analizador = argparse.ArgumentParser(description="Pipeline de la tabla registros (F01 + X01, L01, Q01, G01).")
    analizador.add_argument("--fase", type=int, choices=FASES, help="ejecuta solo esa fase (1, 2, 3 o 4)")
    analizador.add_argument("--completo", action="store_true", help="muestra las tablas PASA / FALLA completas")
    analizador.add_argument("--sin-revision", action="store_true", help="no ejecuta las skills de revisión")
    args = analizador.parse_args()
    COMPLETO, SIN_REVISION = args.completo, args.sin_revision

    for numero in ([args.fase] if args.fase else FASES):
        FASES[numero]()


if __name__ == "__main__":
    main()
