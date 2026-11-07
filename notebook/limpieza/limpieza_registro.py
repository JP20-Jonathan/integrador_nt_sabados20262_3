"""
limpieza_registro.py - HU L01: limpia los datos de `registros` con pandas.

Ejecutar desde la raiz del proyecto:
    python notebook/limpieza/limpieza_registro.py
        lee data/crudo/registros_sucio.csv y guarda data/limpio/registros_limpio.csv

Imprime el diagnostico ANTES y DESPUES de limpiar (shape, info, nulos, duplicados)
y cuantas filas se eliminaron.
"""
import os
import sys

import pandas as pd

RUTA_SUCIO = "data/crudo/registros_sucio.csv"
RUTA_LIMPIO = "data/limpio/registros_limpio.csv"
PAR = ["id_usuario", "id_reto"]


def diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y duplicados exactos de un DataFrame."""
    print(f"===== {titulo} =====")
    print("shape:", df.shape)
    df.info()
    print("nulos por columna:")
    print(df.isna().sum())
    print("duplicados exactos:", df.duplicated().sum())
    print()


def limpiar(df):
    """Aplica la limpieza de la HU L01 (criterios 4 a 10) y devuelve el DataFrame limpio."""
    #4. Quitar los duplicados exactos
    df = df.drop_duplicates().copy()

    #5. Convertir la fecha, que viene en dos formatos mezclados.
    #   Se lee cada formato por separado: con pandas 3, to_datetime(format="mixed", dayfirst=True)
    #   invierte dia y mes en las fechas ISO (2026-03-05 pasa a 2026-05-03).
    iso = pd.to_datetime(df["fecha_registro"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    latino = pd.to_datetime(df["fecha_registro"], format="%d/%m/%Y %H:%M", errors="coerce")
    df["fecha_registro"] = iso.fillna(latino)

    #6. Unificar el estado
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")

    #7. Rellenar las observaciones vacias
    df["observacion"] = df["observacion"].fillna("Sin observacion")

    #8. Detectar las participaciones repetidas (mismo usuario en el mismo reto)
    repetidos = df[df.duplicated(subset=PAR, keep=False)]
    print(f"participaciones repetidas (filas con un par usuario-reto repetido): {len(repetidos)}")

    #9. Dejar solo la primera participacion de cada par
    df = df.drop_duplicates(subset=PAR, keep="first")

    #10. Columna mes para agrupar despues
    df["mes"] = df["fecha_registro"].dt.to_period("M")
    return df


def limpiar_registros(ruta_sucio=RUTA_SUCIO, ruta_limpio=RUTA_LIMPIO):
    """Lee el CSV sucio, lo limpia, imprime antes y despues, y guarda el CSV limpio."""
    #2. Leer el archivo sucio
    df = pd.read_csv(ruta_sucio)

    #3. Diagnostico inicial
    diagnostico(df, "ANTES")
    filas_antes = len(df)

    df = limpiar(df)

    #11. Diagnostico final y filas eliminadas
    diagnostico(df, "DESPUES")
    print(f"filas eliminadas: {filas_antes - len(df)} (de {filas_antes} a {len(df)})")

    #12. Guardar el resultado
    carpeta = os.path.dirname(ruta_limpio)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    df.to_csv(ruta_limpio, index=False, encoding="utf-8")
    print(f"guardado en {ruta_limpio}")
    return df


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    limpiar_registros(*argumentos[:2])
