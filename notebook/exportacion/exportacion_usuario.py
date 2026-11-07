'''
USR-X01 - Exporta los datos sucios de `usuarios` a CSV, Excel y JSON en data/crudo/.
Son los archivos que va a leer la etapa de limpieza.

Ejecutar desde la raiz del proyecto:
    python notebook/exportacion/exportacion_usuario.py
'''

import os
import sys
from pathlib import Path

#1. Importar la simulacion (vive en notebook/simulaciones/); no se copia su codigo
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulaciones"))
from simulacion_usuario import generar_usuarios

#2. Carpeta donde quedan los archivos sucios
CARPETA = "data/crudo"


#3. Genera el DataFrame y lo guarda en los tres formatos
def exportar_usuarios():
    df = generar_usuarios()

    #La carpeta se crea sola si no existe
    os.makedirs("data/crudo", exist_ok=True)

    ruta_csv = f"{CARPETA}/usuarios_sucio.csv"
    ruta_xlsx = f"{CARPETA}/usuarios_sucio.xlsx"
    ruta_json = f"{CARPETA}/usuarios_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="usuarios")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    #Mostrar la ruta y el tamaño de cada archivo generado
    rutas = [ruta_csv, ruta_xlsx, ruta_json]
    for ruta in rutas:
        print(f"{ruta} -> {df.shape}")
    return rutas


if __name__ == "__main__":
    exportar_usuarios()
