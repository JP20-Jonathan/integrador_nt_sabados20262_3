"""HU L01 - Limpia la tabla categorias sucia y guarda la version limpia."""
import os
from pathlib import Path

import pandas as pd

# Rutas del proyecto (funcionan sin importar desde que carpeta se ejecute)
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]      # raiz del proyecto
RUTA_SUCIO = RAIZ_PROYECTO / "data" / "crudo" / "categorias_sucio.csv"
CARPETA_LIMPIO = RAIZ_PROYECTO / "data" / "limpio"
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "descripcion", "area_responsable"]


def diagnosticar(df, momento):
    """Imprime el diagnostico de la tabla: shape, info, nulos y duplicados exactos."""
    print(f"\n--- Diagnostico {momento} ---")
    print(f"df.shape: {df.shape}")
    df.info()
    print(f"df.isna().sum():\n{df.isna().sum()}")
    print(f"df.duplicated().sum(): {df.duplicated().sum()}")


def limpiar(ruta=RUTA_SUCIO):
    """Lee el CSV sucio, corrige cada error de la HU L01, guarda el archivo
    limpio y el catalogo, y devuelve el DataFrame limpio."""
    df = pd.read_csv(ruta)
    filas_antes = len(df)
    diagnosticar(df, "ANTES de limpiar")

    # 1. Quitar los duplicados exactos
    df = df.drop_duplicates()

    # 2. Unificar el nombre: sin espacios sobrantes y con Mayuscula Inicial
    df["nombre"] = df["nombre"].str.strip().str.title()

    # 3. Quitar las tildes para que "logística" y "logistica" queden iguales
    df["nombre"] = df["nombre"].str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("utf-8")

    # 4. Rellenar los nulos
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    df["area_responsable"] = df["area_responsable"].fillna("Sin asignar")

    # 5. Nueva columna con el largo de la descripcion
    df["largo_desc"] = df["descripcion"].str.len()

    # 6. Catalogo real: una fila por categoria
    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    catalogo = df.drop_duplicates(subset=["nombre"])
    catalogo.to_csv(CARPETA_LIMPIO / "categorias_catalogo.csv", index=False, encoding="utf-8")
    print(f"\nCatalogo real: {len(catalogo)} categorias -> {sorted(catalogo['nombre'])}")

    # 7. Diagnostico final y filas eliminadas
    diagnosticar(df, "DESPUES de limpiar")
    print(f"\nFilas antes: {filas_antes} | Filas despues: {len(df)} | "
          f"Filas eliminadas: {filas_antes - len(df)}")

    # 8. Guardar el resultado
    ruta_limpio = CARPETA_LIMPIO / "categorias_limpio.csv"
    df.to_csv(ruta_limpio, index=False, encoding="utf-8")
    print(f"Guardado: {ruta_limpio.relative_to(RAIZ_PROYECTO)}")
    return df


if __name__ == "__main__":
    limpiar()