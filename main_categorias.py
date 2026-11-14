"""Punto de entrada del proyecto integrador.
Prueba las HU F01 (simulacion), X01 (exportacion), L01 (limpieza),
Q01 (consultas) y G01 (graficas) de la tabla categorias.

Ejecutar desde la raiz del proyecto:
    python main_categorias.py
"""
import pandas as pd

from src.notebook.consultas.consulta_categorias import ejecutar_consultas
from src.notebook.exportacion.exportacion_categorias import exportar
from src.notebook.graficas.reporte_categorias import generar_reporte
from src.notebook.limpieza.limpieza_categorias import COLUMNAS_OBLIGATORIAS, limpiar
from src.notebook.simulaciones.simulacion_categorias import FILAS, generar_categorias

COLUMNAS = ["id", "nombre", "descripcion", "area_responsable"]


def titulo(texto):
    """Imprime un titulo para separar cada prueba en la consola."""
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def probar_simulacion():
    """HU F01: genera la tabla sucia y muestra que quedo como pide la HU."""
    titulo("HU F01 - Simulacion de categorias")
    df = generar_categorias()
    print(f"Tamano: {df.shape}  (esperado: ({FILAS}, {len(COLUMNAS)}))")
    print(f"Columnas: {list(df.columns)}")
    print(f"\nNulos por columna:\n{df.isna().sum()}")
    print(f"\nDuplicados exactos: {df.duplicated().sum()}")
    logistica = sorted(df.loc[df['nombre'].str.strip().str.lower()
                              .isin(['logistica', 'logística']), 'nombre'].unique())
    print(f"Variantes de Logistica: {logistica}")
    return df


def probar_exportacion(df):
    """HU X01: exporta los tres archivos y los vuelve a leer para comprobarlos."""
    titulo("HU X01 - Exportacion de categorias")
    rutas = exportar(df)

    print("\nLectura de comprobacion:")
    leidos = {
        "csv": pd.read_csv(rutas["csv"], encoding="utf-8"),
        "xlsx": pd.read_excel(rutas["xlsx"], sheet_name="categorias"),
        "json": pd.read_json(rutas["json"], orient="records"),
    }
    for formato, datos in leidos.items():
        ok = datos.shape == df.shape and list(datos.columns) == COLUMNAS
        print(f"  {formato:<5} {datos.shape}  {'OK' if ok else 'REVISAR'}")


def probar_limpieza():
    """HU L01: limpia el CSV exportado y comprueba que no queden nulos,
    duplicados exactos ni variantes de escritura."""
    titulo("HU L01 - Limpieza de categorias")
    df = limpiar()

    print("\nComprobacion:")
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    reales = df["nombre"].nunique()
    print(f"  Nulos en columnas obligatorias: {nulos}  {'OK' if nulos == 0 else 'REVISAR'}")
    print(f"  Duplicados exactos:             {duplicados}  {'OK' if duplicados == 0 else 'REVISAR'}")
    print(f"  Categorias reales:              {reales}  {'OK' if reales == 10 else 'REVISAR'}")
    print(f"  Columna largo_desc:             {'OK' if 'largo_desc' in df.columns else 'FALTA'}")
    return df


def probar_consultas():
    """HU Q01: ejecuta las cinco consultas y comprueba que se guardaron los CSV."""
    titulo("HU Q01 - Consultas de categorias")
    resultados = ejecutar_consultas()

    print("\nComprobacion:")
    print(f"  Consultas ejecutadas: {len(resultados)}  {'OK' if len(resultados) == 5 else 'REVISAR'}")
    print(f"  Categorias en la consulta 1: {len(resultados[1])}  "
          f"{'OK' if len(resultados[1]) == 10 else 'REVISAR'}")
    print(f"  Filas sin descripcion (consulta 2): {len(resultados[2])}")
    return resultados


def probar_graficas():
    """HU G01: crea las graficas, imprime las conclusiones y comprueba
    que las imagenes quedaron guardadas en reportes/."""
    titulo("HU G01 - Graficas y conclusiones de categorias")
    rutas = generar_reporte()

    print("\nComprobacion:")
    for ruta in rutas:
        print(f"  {ruta.name}  {'OK' if ruta.is_file() else 'FALTA'}")
    return rutas


def main():
    """Ejecuta las pruebas de las HU F01, X01, L01, Q01 y G01 en orden."""
    df = probar_simulacion()
    probar_exportacion(df)
    probar_limpieza()
    probar_consultas()
    probar_graficas()
    titulo("Listo")


if __name__ == "__main__":
    main()