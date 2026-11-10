"""HU Q01 - Cinco consultas sobre la tabla categorias limpia."""
import os
from pathlib import Path

import pandas as pd

# Rutas del proyecto (funcionan sin importar desde que carpeta se ejecute)
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]      # raiz del proyecto
CARPETA_LIMPIO = RAIZ_PROYECTO / "data" / "limpio"
RUTA_LIMPIO = CARPETA_LIMPIO / "categorias_limpio.csv"


def titulo(numero, pregunta):
    """Imprime el encabezado de una consulta con la pregunta que responde."""
    print(f"\n--- Consulta {numero}: {pregunta} ---")


def consulta_1(df):
    """Consulta 1: cuantas veces aparece cada categoria (detecta las variantes)."""
    titulo(1, "¿Cuantas veces aparece cada categoria?")
    conteo = df["nombre"].value_counts()
    print(conteo.to_string())
    return conteo


def consulta_2(df):
    """Consulta 2: categorias que quedaron sin descripcion."""
    titulo(2, "¿Que categorias no tienen descripcion?")
    sin_desc = df[df["descripcion"] == "Sin descripcion"]
    print(f"Total: {len(sin_desc)} filas")
    print(sin_desc[["id", "nombre", "area_responsable"]].to_string(index=False))
    return sin_desc


def consulta_3(df):
    """Consulta 3 (groupby): largo promedio de la descripcion por categoria."""
    titulo(3, "¿Cual es el largo promedio de la descripcion por categoria?")
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    print(largos.to_string())
    return largos


def consulta_4(df):
    """Consulta 4 (groupby): cuantas categorias maneja cada area."""
    titulo(4, "¿Cuantas categorias maneja cada area?")
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    print(por_area.to_string())
    return por_area


def consulta_5(df):
    """Consulta 5 (groupby doble): tabla cruzada de categorias por area."""
    titulo(5, "¿Cuantas filas de cada categoria tiene cada area?")
    tabla = df.groupby(["area_responsable", "nombre"])["id"].count().unstack(fill_value=0)
    print(tabla.to_string())
    return tabla


def guardar(resultado, numero):
    """Guarda el resultado de la consulta N en data/limpio/categorias_consulta_N.csv.
    Las tablas agrupadas se pasan a columnas con reset_index() para no
    perder la categoria o el area."""
    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    ruta = CARPETA_LIMPIO / f"categorias_consulta_{numero}.csv"
    if isinstance(resultado, pd.Series) or resultado.index.name is not None:
        resultado = resultado.reset_index()
    resultado.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def ejecutar_consultas(ruta=RUTA_LIMPIO):
    """Lee el archivo LIMPIO, ejecuta las cinco consultas en orden, guarda
    cada resultado y devuelve un diccionario {numero: resultado}."""
    df = pd.read_csv(ruta)
    consultas = [consulta_1, consulta_2, consulta_3, consulta_4, consulta_5]
    resultados = {}
    for numero, consulta in enumerate(consultas, start=1):
        resultados[numero] = consulta(df)
        ruta_csv = guardar(resultados[numero], numero)
        print(f"Guardado: {ruta_csv.relative_to(RAIZ_PROYECTO)}")
    return resultados


if __name__ == "__main__":
    ejecutar_consultas()