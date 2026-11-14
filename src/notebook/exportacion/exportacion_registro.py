'''
Exporta los datos sucios de `registros` a CSV, Excel y JSON en data/crudo/.
Son los archivos que va a leer la etapa de limpieza.

Ejecutar desde la raíz del proyecto:
    python src/notebook/exportacion/exportacion_registro.py
'''

import os
import sys
from pathlib import Path

#1. Poder importar la simulación, que vive en src/notebook/simulaciones/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulaciones"))
from simulacion_registro import generar_registros

#2. Carpeta donde quedan los archivos sucios
CARPETA = "data/crudo"


#3. Función que genera el DataFrame y lo guarda en los tres formatos
def exportar():
    df = generar_registros()

    #La carpeta se crea sola si no existe
    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = f"{CARPETA}/registros_sucio.csv"
    ruta_xlsx = f"{CARPETA}/registros_sucio.xlsx"
    ruta_json = f"{CARPETA}/registros_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="registros")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    #Mostrar la ruta y el tamaño de cada archivo generado
    rutas = [ruta_csv, ruta_xlsx, ruta_json]
    for ruta in rutas:
        print(f"{ruta} -> {df.shape}")
    return rutas


if __name__ == "__main__":
    exportar()
