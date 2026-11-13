"""HU L01 - Limpia la tabla retos sucia y guarda la version limpia."""
import os
from pathlib import Path

import pandas as pd

# Rutas del proyecto (funcionan sin importar desde que carpeta se ejecute)
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]      # raiz del proyecto
RUTA_SUCIO = RAIZ_PROYECTO / "data" / "crudo" / "retos_sucio.csv"
CARPETA_LIMPIO = RAIZ_PROYECTO / "data" / "limpio"
COLUMNAS_OBLIGATORIAS = ["estado", "descripcion", "fecha_inicio", "fecha_fin"]


def diagnosticar(df, momento):
    """Imprime el diagnostico de la tabla: shape, info, nulos y duplicados exactos."""
    print(f"\n--- Diagnostico {momento} ---")
    print(f"df.shape: {df.shape}")
    df.info()
    print(f"df.isna().sum():\n{df.isna().sum()}")
    print(f"df.duplicated().sum(): {df.duplicated().sum()}")


def parsear_fechas(serie):
    """Convierte una serie de texto a datetime aceptando dos formatos.

    Las fechas ISO (AAAA-MM-DD) se leen aparte porque con dayfirst=True
    pandas las interpretaria al reves. El resto (DD/MM/AAAA) usa
    format="mixed" y dayfirst=True. Lo que no se pueda interpretar queda NaT.
    """
    serie = serie.astype("string").str.strip()
    es_iso = serie.str.match(r"^\d{4}-\d{2}-\d{2}", na=False)
    iso = pd.to_datetime(serie.where(es_iso), format="ISO8601", errors="coerce")
    otros = pd.to_datetime(
        serie.where(~es_iso), format="mixed", dayfirst=True, errors="coerce"
    )
    return iso.fillna(otros)


def limpiar(ruta=RUTA_SUCIO):
    """Lee el CSV sucio, corrige cada error de la HU L01, guarda el archivo
    limpio y devuelve el DataFrame limpio."""
    df = pd.read_csv(ruta)
    filas_antes = len(df)
    diagnosticar(df, "ANTES de limpiar")

    # 1. Quitar los duplicados exactos
    df = df.drop_duplicates()

    # 2. Convertir las fechas (dos formatos posibles)
    for columna in ["fecha_inicio", "fecha_fin"]:
        df[columna] = parsear_fechas(df[columna])

    # 3. Unificar el estado: sin espacios, en mayusculas y con guion bajo
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")

    # 4. Rellenar las descripciones vacias
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")

    # 5. Calcular duracion y marcar fechas incoherentes
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    df["fecha_valida"] = df["duracion_dias"] >= 0

    diagnosticar(df, "DESPUES de limpiar")
    print(f"\nFilas antes: {filas_antes} | Filas despues: {len(df)} | "
          f"Filas eliminadas: {filas_antes - len(df)}")

    incoherentes = int((~df["fecha_valida"]).sum())
    print(f"Fechas incoherentes (fin antes que inicio): {incoherentes}")

    pendientes = df[COLUMNAS_OBLIGATORIAS].isna().sum()
    pendientes = {c: int(n) for c, n in pendientes.items() if n > 0}
    if pendientes:
        print(f"\nAVISO: quedan nulos en columnas obligatorias: {pendientes}")

    # 6. Guardar el resultado
    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    ruta_limpio = CARPETA_LIMPIO / "retos_limpio.csv"
    df.to_csv(ruta_limpio, index=False, encoding="utf-8")
    print(f"Guardado: {ruta_limpio.relative_to(RAIZ_PROYECTO)}")
    return df


if __name__ == "__main__":
    limpiar()
