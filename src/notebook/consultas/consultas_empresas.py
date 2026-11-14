"""HU Q01 - Consultas sobre la tabla empresas.

Lee   data/limpio/empresas_limpio.csv (el archivo LIMPIO, no el sucio)
Guarda data/limpio/empresas_consulta_1.csv ... empresas_consulta_5.csv

Se puede ejecutar solo (desde la raíz del proyecto):
    python src/notebook/consultas/consultas_empresas.py
o desde main_empresa.py:
    python main_empresa.py
"""

import os

import pandas as pd

# Rutas: este archivo está en <raiz>/src/notebook/consultas/
CARPETA_CONSULTAS = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(CARPETA_CONSULTAS)))

CARPETA_LIMPIO = os.path.join(RAIZ_PROYECTO, "data", "limpio")
RUTA_LIMPIO = os.path.join(CARPETA_LIMPIO, "empresas_limpio.csv")

# Sector de la consulta 2. La HU usa 'Logistica' de ejemplo, pero en nuestra
# simulación no existe; 'Transporte' es el sector equivalente.
SECTOR_CONSULTA_2 = "Transporte"


def leer_limpio():
    """Lee el CSV limpio. nit y telefono como texto para no perder ceros a la izquierda."""
    df = pd.read_csv(RUTA_LIMPIO, dtype={"nit": str, "telefono": str}, encoding="utf-8")
    # Por si activa llega como texto, se asegura que sea booleano.
    if df["activa"].dtype != bool:
        df["activa"] = df["activa"].astype(str).str.strip().str.upper().map({"TRUE": True, "FALSE": False})
    return df


def consulta_1_activas(df):
    """Consulta 1: solo las empresas activas."""
    print("Consulta 1 - ¿Cuáles empresas están activas?")
    activas = df[df["activa"] == True]  # noqa: E712 (igual que en la HU)
    return activas


def consulta_2_sector_ordenado(df):
    """Consulta 2: empresas de un sector, ordenadas por nombre."""
    print(f"Consulta 2 - ¿Cuáles empresas son del sector {SECTOR_CONSULTA_2}, ordenadas por nombre?")
    sector = df[df["sector"] == SECTOR_CONSULTA_2].sort_values("nombre")
    return sector


def consulta_3_conteo_rapido(df):
    """Consulta 3: cuántas empresas hay por sector (conteo rápido con value_counts)."""
    print("Consulta 3 - ¿Cuántas empresas hay por sector? (conteo rápido)")
    conteo = df["sector"].value_counts()
    return conteo


def consulta_4_groupby_sector(df):
    """Consulta 4 (GROUPBY): empresas por sector, de mayor a menor."""
    print("Consulta 4 - ¿Cuántas empresas hay por sector, de mayor a menor? (groupby)")
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    return por_sector


def consulta_5_groupby_doble(df):
    """Consulta 5 (GROUPBY doble): empresas activas e inactivas por sector."""
    print("Consulta 5 - ¿Cuántas empresas activas e inactivas hay por sector? (groupby doble)")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    return tabla


def mostrar_y_guardar(resultado, numero):
    """Imprime el resultado y lo guarda como data/limpio/empresas_consulta_N.csv."""
    if isinstance(resultado, pd.Series):
        resultado = resultado.to_frame()

    if resultado.empty:
        print("(sin resultados)")
    elif numero <= 2:
        # Consultas 1 y 2 devuelven filas completas: se muestran columnas clave.
        print(f"{len(resultado)} empresas")
        print(resultado[["nombre", "nit", "sector", "activa"]].to_string(index=False))
    else:
        print(resultado.to_string())

    destino = os.path.join(CARPETA_LIMPIO, f"empresas_consulta_{numero}.csv")
    # Consultas 1 y 2 conservan filas completas; las demás usan el sector como índice.
    resultado.to_csv(destino, index=numero >= 3, encoding="utf-8")
    print(f"-> Guardado en {os.path.relpath(destino, RAIZ_PROYECTO)}\n")


def consultar_empresas():
    """Ejecuta las cinco consultas en orden y guarda cada resultado."""
    df = leer_limpio()
    consultas = [
        consulta_1_activas,
        consulta_2_sector_ordenado,
        consulta_3_conteo_rapido,
        consulta_4_groupby_sector,
        consulta_5_groupby_doble,
    ]
    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        mostrar_y_guardar(resultado, numero)


if __name__ == "__main__":
    consultar_empresas()