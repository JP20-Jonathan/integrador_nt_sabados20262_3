"""HU X01 - Exporta la tabla empresas sucia a CSV, Excel y JSON.

Se puede ejecutar solo (desde la raíz del proyecto):
    python notebook/exportacion/exportar_empresas.py
o desde main_empresa.py:
    python main_empresa.py
"""

import os
import sys
from importlib import import_module

# Rutas: este archivo está en <raiz>/notebook/exportacion/
CARPETA_EXPORTACIONES = os.path.dirname(os.path.abspath(__file__))
CARPETA_NOTEBOOK = os.path.dirname(CARPETA_EXPORTACIONES)
RAIZ_PROYECTO = os.path.dirname(CARPETA_NOTEBOOK)

# Los archivos siempre quedan en <raiz>/data/crudo, sin importar desde dónde se ejecute.
CARPETA_CRUDO = os.path.join(RAIZ_PROYECTO, "data", "crudo")

# Permite importar la carpeta simulaciones aunque se ejecute este archivo solo.
if CARPETA_NOTEBOOK not in sys.path:
    sys.path.insert(0, CARPETA_NOTEBOOK)

# Se importa la función de la HU F01; NO se copia el código de generación.
generar_empresas = import_module("simulaciones.simular_empresas").generar_empresas


def exportar():
    df = generar_empresas(n=300)

    # La carpeta se crea sola si no existe.
    os.makedirs(CARPETA_CRUDO, exist_ok=True)

    ruta_csv = os.path.join(CARPETA_CRUDO, "empresas_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA_CRUDO, "empresas_sucio.xlsx")
    ruta_json = os.path.join(CARPETA_CRUDO, "empresas_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="empresas")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{os.path.relpath(ruta, RAIZ_PROYECTO)} -> {df.shape}")

    return df


if __name__ == "__main__":
    exportar()