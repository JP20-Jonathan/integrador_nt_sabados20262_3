"""HU L01 - Limpia la tabla empresas.

Lee  data/crudo/empresas_sucio.csv
Guarda data/limpio/empresas_limpio.csv

Se puede ejecutar solo (desde la raíz del proyecto):
    python src/notebook/limpieza/limpiar_empresas.py
o desde main_empresa.py:
    python main_empresa.py
"""

import os

import pandas as pd

# Rutas: este archivo está en <raiz>/src/notebook/limpieza/
CARPETA_LIMPIEZAS = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(CARPETA_LIMPIEZAS)))

RUTA_SUCIO = os.path.join(RAIZ_PROYECTO, "data", "crudo", "empresas_sucio.csv")
CARPETA_LIMPIO = os.path.join(RAIZ_PROYECTO, "data", "limpio")
RUTA_LIMPIO = os.path.join(CARPETA_LIMPIO, "empresas_limpio.csv")

# Columnas que no pueden quedar con nulos después de limpiar.
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "nit", "sector", "contacto", "correo", "telefono", "activa"]

# Valores de texto aceptados para la columna activa.
MAPA_ACTIVA = {
    "TRUE": True, "SI": True, "SÍ": True, "1": True,
    "FALSE": False, "NO": False, "0": False,
}

# Sectores válidos tal como deben quedar escritos.
# Se buscan en minúscula para que 'SALUD', ' salud ' y 'Salud' queden igual.
SECTORES = ["Tecnología", "Salud", "Educación", "Finanzas", "Manufactura", "Energía",
            "Transporte", "Turismo", "Alimentos y Bebidas", "Medios y Entretenimiento"]
MAPA_SECTORES = {sector.lower(): sector for sector in SECTORES}


def normalizar_nombre(nombre):
    """Pasa a formato título los nombres que llegaron en MAYÚSCULAS.
    'ACOSTA LLC' -> 'Acosta LLC', 'SUÁREZ AND SONS' -> 'Suárez and Sons'."""
    if nombre != nombre.upper():
        return nombre  # ya viene bien escrito
    nombre = nombre.title()
    return nombre.replace(" And ", " and ").replace("Llc", "LLC")


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y duplicados exactos."""
    print(f"\n{'=' * 60}\n{titulo}\n{'=' * 60}")
    print("Shape:", df.shape, "\n")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def limpiar(df):
    """Aplica en orden cada corrección que piden los criterios de la HU L01."""
    # 1. Quitar los duplicados exactos.
    df = df.drop_duplicates().copy()

    # 2. Quitar los espacios sobrantes del nombre y corregir los que están en MAYÚSCULAS.
    df["nombre"] = df["nombre"].str.strip().map(normalizar_nombre)

    # 3. Unificar el sector ('SALUD' y ' salud ' quedan como 'Salud').
    #    No se usa .title() porque cambiaría 'Alimentos y Bebidas' por 'Alimentos Y Bebidas'.
    sector_minuscula = df["sector"].str.strip().str.lower()
    df["sector"] = sector_minuscula.map(MAPA_SECTORES).fillna(df["sector"].str.strip().str.title())

    # 4. Dejar el nit en un solo formato (sin puntos ni guiones).
    df["nit"] = df["nit"].str.replace(r"[.\-]", "", regex=True)

    # 5. Dejar el teléfono solo con dígitos y sin el indicativo del país
    #    ('+57 300-123-4567' y '300 123 4567' -> '3001234567').
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)
    df["telefono"] = df["telefono"].str.replace(r"^57(?=\d{10}$)", "", regex=True)

    # 6. Convertir activa a booleano de verdad (al leer el CSV llega como texto).
    df["activa"] = df["activa"].astype(str).str.strip().str.upper().map(MAPA_ACTIVA)

    # 7. Rellenar los contactos vacíos con "Sin contacto".
    df["contacto"] = df["contacto"].fillna("Sin contacto")

    # 8. Marcar los correos inválidos en una columna nueva.
    df["correo_valido"] = df["correo"].str.contains("@", na=False)

    # 9. Al normalizar pueden aparecer duplicados nuevos; se quitan otra vez.
    df = df.drop_duplicates()

    # 10. Marcar los nit repetidos entre empresas distintas (no se borran porque
    #     son empresas diferentes; hay que revisarlas a mano).
    df["nit_repetido"] = df["nit"].duplicated(keep=False)

    return df


def verificar(df):
    """Comprueba que no quedan nulos en las columnas obligatorias ni duplicados exactos."""
    nulos = df[COLUMNAS_OBLIGATORIAS].isna().sum()
    nulos = nulos[nulos > 0]
    duplicados = df.duplicated().sum()
    if nulos.empty and duplicados == 0:
        print("\nVerificación OK: sin nulos en columnas obligatorias y sin duplicados exactos.")
        return True
    print("\nATENCIÓN: la limpieza no quedó completa.")
    if not nulos.empty:
        print("Nulos en columnas obligatorias:\n", nulos)
    if duplicados:
        print("Duplicados exactos restantes:", duplicados)
    return False


def limpiar_empresas():
    """Lee el CSV sucio, lo limpia, imprime el antes y el después y guarda el CSV limpio."""
    # nit y telefono se leen como texto para no perder ceros a la izquierda.
    df = pd.read_csv(RUTA_SUCIO, dtype={"nit": str, "telefono": str}, encoding="utf-8")
    filas_iniciales = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = limpiar(df)

    print(f"\n{'=' * 60}\nDIAGNÓSTICO DESPUÉS DE LIMPIAR\n{'=' * 60}")
    print("Shape:", df.shape)
    print("\nNulos por columna:")
    print(df.isna().sum())
    print(f"\nFilas eliminadas: {filas_iniciales - len(df)} (de {filas_iniciales} a {len(df)})")
    verificar(df)

    # La carpeta se crea sola si no existe.
    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    df.to_csv(RUTA_LIMPIO, index=False, encoding="utf-8")
    print("\nArchivo guardado en:", os.path.relpath(RUTA_LIMPIO, RAIZ_PROYECTO))

    return df


if __name__ == "__main__":
    limpiar_empresas()