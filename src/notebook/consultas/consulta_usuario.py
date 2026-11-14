"""
consulta_usuario.py - USR-Q01: cinco consultas sobre `usuarios` con pandas (dos con groupby).

Ejecutar desde la raiz del proyecto:
    python src/notebook/consultas/consulta_usuario.py
        lee data/limpio/usuarios_limpio.csv y guarda data/limpio/usuarios_consulta_N.csv

Cada consulta va en su propia funcion, imprime que pregunta responde y su resultado,
y guarda la respuesta en usuarios_consulta_N.csv.
"""
import os
import sys

import pandas as pd

RUTA_LIMPIO = "data/limpio/usuarios_limpio.csv"
CARPETA_SALIDA = "data/limpio"


def guardar(resultado, numero, carpeta, nombre_valor=None, con_indice=False):
    """Guarda el resultado de una consulta en usuarios_consulta_N.csv."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = f"{carpeta}/usuarios_consulta_{numero}.csv"
    if isinstance(resultado, pd.Series):
        resultado.rename(nombre_valor).to_csv(ruta, encoding="utf-8")
    else:
        resultado.to_csv(ruta, index=con_indice, encoding="utf-8")
    print(f"-> guardado en {ruta}\n")


def consulta_1(df, carpeta):
    """Consulta 1: usuarios activos."""
    print("CONSULTA 1 - ¿Qué usuarios están activos?")
    activos = df[df["activo"] == True]  # noqa: E712 (es la línea de la HU)
    print(f"{len(activos)} usuarios activos de {len(df)}. Primeras filas:")
    print(activos.head())
    guardar(activos, 1, carpeta)
    return activos


def consulta_2(df, carpeta):
    """Consulta 2: solo los administradores, ordenados por nombre."""
    print("CONSULTA 2 - ¿Quiénes son los administradores? (ordenados por nombre)")
    admins = df[df["rol"] == "ADMIN"].sort_values("nombre")
    print(f"{len(admins)} administradores. Primeras filas:")
    print(admins[["nombre", "correo", "activo"]].head())
    guardar(admins, 2, carpeta)
    return admins


def consulta_3(df, carpeta):
    """Consulta 3: los 5 dominios de correo mas comunes."""
    print("CONSULTA 3 - ¿Cuáles son los 5 dominios de correo más comunes?")
    dominios = df["correo"].str.split("@").str[1].value_counts().head(5)
    print(dominios)
    guardar(dominios, 3, carpeta, "usuarios")
    return dominios


def consulta_4(df, carpeta):
    """Consulta 4 (groupby doble): activos e inactivos por rol."""
    print("CONSULTA 4 - ¿Cuántos usuarios activos e inactivos hay por rol? (groupby)")
    tabla = df.groupby(["rol", "activo"])["id"].count().unstack(fill_value=0)
    print(tabla)
    guardar(tabla, 4, carpeta, con_indice=True)
    return tabla


def consulta_5(df, carpeta):
    """Consulta 5 (groupby por mes): cuantos usuarios se registraron cada mes."""
    print("CONSULTA 5 - ¿Cuántos usuarios se registraron cada mes? (groupby)")
    por_mes = df.groupby("mes")["id"].count()
    print(por_mes)
    guardar(por_mes, 5, carpeta, "usuarios")
    return por_mes


def consultar_usuarios(ruta_limpio=RUTA_LIMPIO, carpeta=CARPETA_SALIDA):
    """Lee el CSV limpio y ejecuta las cinco consultas en orden."""
    df = pd.read_csv(ruta_limpio)
    print(f"Leyendo {ruta_limpio}: {df.shape[0]} filas, {df.shape[1]} columnas\n")
    for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5):
        consulta(df, carpeta)


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    consultar_usuarios(*argumentos[:2])
