"""HU Q01 - Cinco consultas sobre la tabla retos limpia."""
import os
from pathlib import Path

import pandas as pd

# Rutas del proyecto (funcionan sin importar desde que carpeta se ejecute)
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]      # raiz del proyecto
CARPETA_LIMPIO = RAIZ_PROYECTO / "data" / "limpio"
RUTA_LIMPIO = CARPETA_LIMPIO / "retos_limpio.csv"


def titulo(numero, pregunta):
    """Imprime el encabezado de una consulta con la pregunta que responde."""
    print(f"\n--- Consulta {numero}: {pregunta} ---")


def consulta_1(df):
    """Consulta 1: retos que estan en curso (filtro por estado EN_CURSO)."""
    titulo(1, "¿Que retos estan en curso?")
    en_curso = df[df["estado"] == "EN_CURSO"]
    print(f"Total: {len(en_curso)} retos")
    print(en_curso[["id", "nombre", "estado"]].to_string(index=False))
    return en_curso


def consulta_2(df):
    """Consulta 2: los 10 retos mas largos (mayor duracion_dias)."""
    titulo(2, "¿Cuales son los 10 retos mas largos?")
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    print(largos.to_string(index=False))
    return largos


def consulta_3(df):
    """Consulta 3: cuantos retos hay por estado (conteo con value_counts)."""
    titulo(3, "¿Cuantos retos hay por estado?")
    conteo = df["estado"].value_counts()
    conteo = conteo.rename_axis("estado").reset_index(name="cantidad")
    print(conteo.to_string(index=False))
    return conteo


def consulta_4(df):
    """Consulta 4 (groupby): duracion promedio, minima y maxima por estado."""
    titulo(4, "¿Cual es la duracion promedio, minima y maxima por estado?")
    resumen = df.groupby("estado")["duracion_dias"].agg(["count", "mean", "min", "max"])
    resumen["mean"] = resumen["mean"].round(2)
    resumen = resumen.reset_index()
    print(resumen.to_string(index=False))
    return resumen


def consulta_5(df):
    """Consulta 5 (groupby): cuantos retos empiezan cada mes."""
    titulo(5, "¿Cuantos retos empiezan cada mes?")
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    por_mes = por_mes.rename_axis("mes").reset_index(name="cantidad")
    por_mes["mes"] = por_mes["mes"].astype(str)
    print(por_mes.to_string(index=False))
    return por_mes


def guardar(resultado, numero):
    """Guarda el resultado de la consulta N en data/limpio/retos_consulta_N.csv."""
    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    ruta = CARPETA_LIMPIO / f"retos_consulta_{numero}.csv"
    if isinstance(resultado, pd.Series) or resultado.index.name is not None:
        resultado = resultado.reset_index()
    resultado.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def ejecutar_consultas(ruta=RUTA_LIMPIO):
    """Lee el archivo limpio, ejecuta las cinco consultas en orden, guarda
    cada resultado y devuelve un diccionario {numero: resultado}."""
    df = pd.read_csv(ruta)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["duracion_dias"] = pd.to_numeric(df["duracion_dias"], errors="coerce")

    consultas = [consulta_1, consulta_2, consulta_3, consulta_4, consulta_5]
    resultados = {}
    for numero, consulta in enumerate(consultas, start=1):
        resultados[numero] = consulta(df)
        ruta_csv = guardar(resultados[numero], numero)
        print(f"Guardado: {ruta_csv.relative_to(RAIZ_PROYECTO)}")
    return resultados


if __name__ == "__main__":
    ejecutar_consultas()
