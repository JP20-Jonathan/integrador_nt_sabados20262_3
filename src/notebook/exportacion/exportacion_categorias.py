"""HU X01 - Exporta la tabla categorias sucia a CSV, Excel y JSON."""
import os
import sys
from importlib import import_module
from pathlib import Path

# Rutas del proyecto (funcionan sin importar desde que carpeta se ejecute)
CARPETA_NOTEBOOK = Path(__file__).resolve().parents[1]   # notebook
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]      # raiz del proyecto
CARPETA = RAIZ_PROYECTO / "data" / "crudo"

# Permite importar la carpeta `simulaciones` aunque este archivo se ejecute solo
if str(CARPETA_NOTEBOOK) not in sys.path:
    sys.path.insert(0, str(CARPETA_NOTEBOOK))

# Importa la funcion de la HU F01 sin copiar el codigo de generacion
generar_categorias = import_module("simulaciones.simulacion_categorias").generar_categorias


def exportar(df=None):
    """Guarda la tabla sucia en los tres formatos de la HU.
    Si no recibe un DataFrame, lo genera con generar_categorias().
    Devuelve un diccionario {formato: ruta} con los archivos creados."""
    os.makedirs(CARPETA, exist_ok=True)
    if df is None:
        df = generar_categorias()

    rutas = {
        "csv": CARPETA / "categorias_sucio.csv",
        "xlsx": CARPETA / "categorias_sucio.xlsx",
        "json": CARPETA / "categorias_sucio.json",
    }
    df.to_csv(rutas["csv"], index=False, encoding="utf-8")
    df.to_excel(rutas["xlsx"], index=False, sheet_name="categorias")
    df.to_json(rutas["json"], orient="records", force_ascii=False, indent=2)

    for ruta in rutas.values():
        print(f"{ruta.relative_to(RAIZ_PROYECTO)} -> {df.shape}")
    return rutas


if __name__ == "__main__":
    exportar()