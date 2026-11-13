"""Punto de entrada del proyecto integrador - tabla empresas.

Ejecuta en orden:
    1. HU F01 + X01: simula los datos sucios y los exporta a data/crudo/
    2. HU L01: limpia los datos y guarda data/limpio/empresas_limpio.csv
    3. HU Q01: hace las cinco consultas y guarda data/limpio/empresas_consulta_N.csv
    4. HU G01: crea las tres gráficas en reportes/ e imprime las conclusiones

Ejecutar desde la raíz del proyecto, con el .venv activado:
    python main_empresa.py
"""

import os

import pandas as pd

from src.notebook.exportacion.exportar_empresas import CARPETA_CRUDO, exportar
from src.notebook.limpieza.limpiar_empresas import limpiar_empresas
from src.notebook.consultas.consultas_empresas import consultar_empresas
from src.notebook.graficas.graficar_empresas import CARPETA_REPORTES, graficar_empresas

GRAFICAS_ESPERADAS = [
    "empresas_grafica_1.png",
    "empresas_grafica_2.png",
    "empresas_grafica_3.png",
]

# Pon False si NO quieres volver a generar los datos sucios
# (por ejemplo, para limpiar los archivos que ya subiste a GitHub).
GENERAR_DATOS_SUCIOS = True


def paso_simular_y_exportar():
    print("\n######## PASO 1 - HU F01 + X01: simular y exportar empresas ########")
    df = exportar()

    print("\n--- Comprobando los archivos exportados ---")
    lectores = {
        "empresas_sucio.csv": lambda ruta: pd.read_csv(ruta, dtype=str),
        "empresas_sucio.xlsx": lambda ruta: pd.read_excel(ruta, sheet_name="empresas", dtype=str),
        "empresas_sucio.json": lambda ruta: pd.read_json(ruta, orient="records", dtype=False),
    }
    todo_bien = True
    for nombre, leer in lectores.items():
        ruta = os.path.join(CARPETA_CRUDO, nombre)
        if not os.path.isfile(ruta):
            print(f"FALLA  {nombre}: no se generó")
            todo_bien = False
            continue
        leido = leer(ruta)
        ok = leido.shape == df.shape and list(leido.columns) == list(df.columns)
        todo_bien = todo_bien and ok
        print(f"{'PASA ' if ok else 'FALLA'}  {nombre}: {leido.shape}")
    return todo_bien


def paso_limpiar():
    print("\n######## PASO 2 - HU L01: limpiar empresas ########")
    df = limpiar_empresas()

    print("\n--- Muestra de los datos limpios ---")
    print(df.head())
    print("\nSectores:", sorted(df["sector"].unique()))
    print("Valores de activa:", df["activa"].value_counts().to_dict())
    print("Correos inválidos:", (~df["correo_valido"]).sum())
    return df


def paso_consultar():
    print("\n######## PASO 3 - HU Q01: consultas de empresas ########\n")
    consultar_empresas()


def paso_graficar():
    print("\n######## PASO 4 - HU G01: gráficas y conclusiones ########")
    graficar_empresas()

    print("\n--- Comprobando las gráficas guardadas en el proyecto ---")
    print("Carpeta:", CARPETA_REPORTES)
    todo_bien = True
    for nombre in GRAFICAS_ESPERADAS:
        ruta = os.path.join(CARPETA_REPORTES, nombre)
        if os.path.isfile(ruta) and os.path.getsize(ruta) > 0:
            print(f"PASA   {nombre} ({os.path.getsize(ruta) // 1024} KB)")
        else:
            print(f"FALLA  {nombre}: no se guardó")
            todo_bien = False
    return todo_bien


def main():
    if GENERAR_DATOS_SUCIOS:
        if not paso_simular_y_exportar():
            print("\nLa exportación falló; no se ejecuta la limpieza.")
            return
    paso_limpiar()
    paso_consultar()
    if paso_graficar():
        print("\nResultado: proceso terminado, gráficas guardadas en reportes/")
    else:
        print("\nResultado: revisa las gráficas con FALLA")


if __name__ == "__main__":
    main()