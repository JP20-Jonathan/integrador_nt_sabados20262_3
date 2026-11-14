"""Punto de entrada del proyecto integrador.
Prueba las HU F01 (simulacion), X01 (exportacion), L01 (limpieza),
Q01 (consultas) y G01 (graficas) de la tabla retos.

Ejecutar desde la raiz del proyecto:
    python main_retos.py
"""
import pandas as pd

from src.notebook.consultas.consulta_reto import ejecutar_consultas
from src.notebook.exportacion.exportacion_reto import exportar
from src.notebook.graficas.reporte_reto import generar_reporte
from src.notebook.limpieza.limpieza_reto import COLUMNAS_OBLIGATORIAS, limpiar
from src.notebook.simulaciones.simulacion_reto import FILAS, generar_retos

COLUMNAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
    "estado", "id_empresa", "id_categoria", "id_prioridad",
]


def titulo(texto):
    """Imprime un titulo para separar cada prueba en la consola."""
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def probar_simulacion():
    """HU F01: genera la tabla sucia y muestra que quedo como pide la HU."""
    titulo("HU F01 - Simulacion de retos")
    df = generar_retos()
    print(f"Tamano: {df.shape}  (esperado: ({FILAS}, {len(COLUMNAS)}))")
    print(f"Columnas: {list(df.columns)}")
    print(f"\nNulos por columna:\n{df.isna().sum()}")
    print(f"\nDuplicados exactos: {df.duplicated().sum()}")
    estados_raros = df[~df["estado"].isin(["Abierto", "Cerrado", "En curso", "Pendiente"])]["estado"].unique()
    print(f"Variantes sucias de estado: {list(estados_raros)[:5]}")
    return df


def probar_exportacion(df):
    """HU X01: exporta los tres archivos y los vuelve a leer para comprobarlos."""
    titulo("HU X01 - Exportacion de retos")
    rutas = exportar(df)

    print("\nLectura de comprobacion:")
    leidos = {
        "csv": pd.read_csv(rutas["csv"], encoding="utf-8"),
        "xlsx": pd.read_excel(rutas["xlsx"], sheet_name="retos"),
        "json": pd.read_json(rutas["json"], orient="records", dtype=False, convert_dates=False),
    }
    for formato, datos in leidos.items():
        ok = datos.shape == df.shape and list(datos.columns) == COLUMNAS
        print(f"  {formato:<5} {datos.shape}  {'OK' if ok else 'REVISAR'}")


def probar_limpieza():
    """HU L01: limpia el CSV exportado y comprueba que no queden nulos
    ni duplicados exactos."""
    titulo("HU L01 - Limpieza de retos")
    df = limpiar()

    print("\nComprobacion:")
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    incoherentes = int((~df["fecha_valida"]).sum()) if "fecha_valida" in df.columns else "N/A"
    print(f"  Nulos en columnas obligatorias: {nulos}  {'OK' if nulos == 0 else 'REVISAR'}")
    print(f"  Duplicados exactos:             {duplicados}  {'OK' if duplicados == 0 else 'REVISAR'}")
    print(f"  Fechas incoherentes marcadas:   {incoherentes}")
    print(f"  Columna duracion_dias:          {'OK' if 'duracion_dias' in df.columns else 'FALTA'}")
    return df


def probar_consultas():
    """HU Q01: ejecuta las cinco consultas y comprueba que se guardaron los CSV."""
    titulo("HU Q01 - Consultas de retos")
    resultados = ejecutar_consultas()

    print("\nComprobacion:")
    print(f"  Consultas ejecutadas: {len(resultados)}  {'OK' if len(resultados) == 5 else 'REVISAR'}")
    print(f"  Retos EN_CURSO (consulta 1): {len(resultados[1])}")
    print(f"  Retos mas largos (consulta 2): {len(resultados[2])}  "
          f"{'OK' if len(resultados[2]) == 10 else 'REVISAR'}")
    return resultados


def probar_graficas():
    """HU G01: crea las graficas, imprime las conclusiones y comprueba
    que las imagenes quedaron guardadas en reportes/."""
    titulo("HU G01 - Graficas y conclusiones de retos")
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
