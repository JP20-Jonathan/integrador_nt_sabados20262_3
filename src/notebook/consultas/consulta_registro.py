"""
consulta_registro.py - HU Q01: cinco consultas sobre `registros` con pandas (dos con groupby).

Ejecutar desde la raiz del proyecto:
    python src/notebook/consultas/consulta_registro.py
        lee data/limpio/registros_limpio.csv y guarda data/limpio/registros_consulta_N.csv

Cada consulta va en su propia funcion, imprime que pregunta responde y su resultado,
y guarda la respuesta en registros_consulta_N.csv.
"""
import os
import sys

import pandas as pd

RUTA_LIMPIO = "data/limpio/registros_limpio.csv"
CARPETA_SALIDA = "data/limpio"


def guardar(resultado, numero, carpeta, nombre_valor=None):
    """Guarda el resultado de una consulta en registros_consulta_N.csv."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = f"{carpeta}/registros_consulta_{numero}.csv"
    if isinstance(resultado, pd.Series):
        resultado.rename(nombre_valor).to_csv(ruta, encoding="utf-8")
    else:
        resultado.to_csv(ruta, index=False, encoding="utf-8")
    print(f"-> guardado en {ruta}\n")


def consulta_1(df, carpeta):
    """Consulta 1: participaciones ya finalizadas."""
    print("CONSULTA 1 - ¿Qué participaciones ya están finalizadas?")
    finalizados = df[df["estado"] == "FINALIZADO"]
    print(f"{len(finalizados)} participaciones finalizadas. Primeras filas:")
    print(finalizados.head())
    guardar(finalizados, 1, carpeta)
    return finalizados


def consulta_2(df, carpeta):
    """Consulta 2: participaciones repetidas (mismo usuario en el mismo reto)."""
    print("CONSULTA 2 - ¿Qué participaciones están repetidas (mismo usuario en el mismo reto)?")
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    print(f"{len(repetidos)} filas repetidas.")
    if repetidos.empty:
        print("(Es lo esperado: la limpieza ya dejó solo la primera participación de cada par.)")
    else:
        print(repetidos.head())
    guardar(repetidos, 2, carpeta)
    return repetidos


def consulta_3(df, carpeta):
    """Consulta 3: cuantas participaciones hay por estado."""
    print("CONSULTA 3 - ¿Cuántas participaciones hay por estado?")
    conteo = df["estado"].value_counts()
    print(conteo)
    guardar(conteo, 3, carpeta, "participaciones")
    return conteo


def consulta_4(df, carpeta):
    """Consulta 4 (groupby): los 10 retos con mas participantes."""
    print("CONSULTA 4 - ¿Cuáles son los 10 retos con más participantes? (groupby)")
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    print(top_retos)
    guardar(top_retos, 4, carpeta, "participantes")
    return top_retos


def consulta_5(df, carpeta):
    """Consulta 5 (groupby por mes): cuantas participaciones hubo cada mes."""
    print("CONSULTA 5 - ¿Cuántas participaciones hubo cada mes? (groupby)")
    por_mes = df.groupby("mes")["id"].count()
    print(por_mes)
    guardar(por_mes, 5, carpeta, "participaciones")
    return por_mes


def consultar(ruta_limpio=RUTA_LIMPIO, carpeta=CARPETA_SALIDA):
    """Lee el CSV limpio y ejecuta las cinco consultas en orden."""
    df = pd.read_csv(ruta_limpio)
    print(f"Leyendo {ruta_limpio}: {df.shape[0]} filas, {df.shape[1]} columnas\n")
    for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5):
        consulta(df, carpeta)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    consultar(*argumentos[:2])
