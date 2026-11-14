"""
limpieza_usuario.py - USR-L01: limpia los datos de `usuarios` con pandas.

Ejecutar desde la raiz del proyecto:
    python src/notebook/limpieza/limpieza_usuario.py
        lee data/crudo/usuarios_sucio.csv y guarda data/limpio/usuarios_limpio.csv

Imprime el diagnostico ANTES y DESPUES de limpiar (shape, info, nulos, duplicados)
y cuantas filas se eliminaron.
"""
import os
import sys

import pandas as pd

RUTA_SUCIO = "data/crudo/usuarios_sucio.csv"
RUTA_LIMPIO = "data/limpio/usuarios_limpio.csv"


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
    """Aplica la limpieza de la HU USR-L01 (criterios 4 a 13) y devuelve el DataFrame limpio."""
    #4. Quitar los duplicados exactos
    df = df.drop_duplicates().copy()

    #5. Normalizar el nombre
    df["nombre"] = df["nombre"].str.strip().str.title()

    #6. Normalizar el correo
    df["correo"] = df["correo"].str.strip().str.lower()

    #7. El correo es obligatorio: quitar las filas sin correo
    filas = len(df)
    df = df.dropna(subset=["correo"])
    print(f"filas sin correo eliminadas: {filas - len(df)}")

    #8. Marcar los correos invalidos (sin arroba)
    df["correo_valido"] = df["correo"].str.contains("@", na=False)
    print(f"correos invalidos (sin @): {int((~df['correo_valido']).sum())}")

    #9. Unificar el rol
    df["rol"] = df["rol"].str.strip().str.upper()

    #10. Convertir activo a booleano de verdad (del CSV llega como texto)
    df["activo"] = df["activo"].astype(str).str.strip().str.upper().map({"TRUE": True, "SI": True, "1": True, "FALSE": False, "NO": False, "0": False})

    #11. Convertir la fecha, que viene en dos formatos mezclados.
    #    Se lee cada formato por separado: con pandas 3, to_datetime(format="mixed", dayfirst=True)
    #    invierte dia y mes en las fechas ISO (2026-03-05 pasa a 2026-05-03).
    iso = pd.to_datetime(df["fecha_registro"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    latino = pd.to_datetime(df["fecha_registro"], format="%d/%m/%Y %H:%M", errors="coerce")
    df["fecha_registro"] = iso.fillna(latino)

    #12. Detectar los correos repetidos y dejar solo el primero
    repetidos = df[df.duplicated(subset=["correo"], keep=False)]
    print(f"correos repetidos (filas que comparten correo con otra): {len(repetidos)}")
    df = df.drop_duplicates(subset=["correo"], keep="first")

    #13. Columna mes para agrupar despues
    df["mes"] = df["fecha_registro"].dt.to_period("M")
    return df


def limpiar_usuarios(ruta_sucio=RUTA_SUCIO, ruta_limpio=RUTA_LIMPIO):
    """Lee el CSV sucio, lo limpia, imprime antes y despues, y guarda el CSV limpio."""
    #2. Leer el archivo sucio
    df = pd.read_csv(ruta_sucio)

    #3. Diagnostico inicial
    diagnostico(df, "ANTES")
    filas_antes = len(df)

    df = limpiar(df)

    #14. Diagnostico final y filas eliminadas
    diagnostico(df, "DESPUES")
    print(f"filas eliminadas: {filas_antes - len(df)} (de {filas_antes} a {len(df)})")

    #15. Guardar el resultado
    carpeta = os.path.dirname(ruta_limpio)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    df.to_csv(ruta_limpio, index=False, encoding="utf-8")
    print(f"guardado en {ruta_limpio}")
    return df


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    limpiar_usuarios(*argumentos[:2])
