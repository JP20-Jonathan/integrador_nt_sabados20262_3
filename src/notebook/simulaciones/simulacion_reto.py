"""HU F01 - Simulacion de la tabla retos con datos sucios a proposito.

Genera 500 filas falsas con Faker y las ensucia (nulos, duplicados, espacios,
formatos mezclados) para practicar la limpieza despues.

Usa Faker("es_CO") y fija la semilla con Faker.seed(42) y random.seed(42)
para que el resultado sea SIEMPRE el mismo y tu companero pueda reproducirlo.
"""

import random
import uuid
from datetime import timedelta

import pandas as pd
from faker import Faker

# 1. Semillas fijas: el resultado es SIEMPRE el mismo.
random.seed(42)
Faker.seed(42)

# 2. Constantes
FILAS = 500
ESTADOS = ["Abierto", "Cerrado", "En curso", "Pendiente"]

# Generador propio (con semilla) para las listas fijas de llaves foraneas.
_RNG_LLAVES = random.Random(42)


def _nuevo_uuid(generador):
    """Devuelve un UUID v4 reproducible usando bits del generador sembrado."""
    return str(uuid.UUID(int=generador.getrandbits(128), version=4))


IDS_EMPRESA = [_nuevo_uuid(_RNG_LLAVES) for _ in range(10)]
IDS_CATEGORIA = [_nuevo_uuid(_RNG_LLAVES) for _ in range(5)]
IDS_PRIORIDAD = [_nuevo_uuid(_RNG_LLAVES) for _ in range(3)]

FALSITO = Faker("es_CO")


def generar_datos(numero_filas=500):
    """Genera numero_filas retos limpios y devuelve una lista de diccionarios."""
    rng_ids = random.Random(43)
    retos = []
    for _ in range(numero_filas):
        fecha_inicio = FALSITO.date_between(start_date="-1y", end_date="+3M")
        retos.append({
            "id": _nuevo_uuid(rng_ids),
            "nombre": FALSITO.sentence(nb_words=6).rstrip("."),
            "descripcion": FALSITO.sentence(nb_words=12),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })
    return retos


def obtener_muestra(datos, porcentaje):
    """Devuelve el indice de un porcentaje de las filas totales."""
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index


def escribir_mal(texto):
    """Devuelve una variante mal escrita del texto."""
    variantes = [texto.lower().replace(" ", "_"), texto.upper(), f" {texto} "]
    return random.choice(variantes)


def ensuciar(datos_df):
    """Ensucia los datos a proposito y devuelve un DataFrame nuevo."""
    datos_df = datos_df.copy()

    # Nombre: el 10% con espacios sobrantes
    filas_elegidas = obtener_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = " " + datos_df.loc[filas_elegidas, "nombre"] + " "

    # Descripcion: el 12% en None (nulos)
    filas_elegidas = obtener_muestra(datos_df, 0.12)
    datos_df.loc[filas_elegidas, "descripcion"] = None

    # Fecha_inicio: dos formatos mezclados: "2026-03-02" y "02/03/2026"
    datos_df["fecha_inicio"] = pd.to_datetime(datos_df["fecha_inicio"])
    iso = datos_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino = datos_df["fecha_inicio"].dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = iso
    filas_elegidas = obtener_muestra(datos_df, 0.25)
    datos_df.loc[filas_elegidas, "fecha_inicio"] = latino.loc[filas_elegidas]

    # Fecha_fin: 8% en None y 5% ANTERIOR a fecha_inicio (error logico a detectar)
    datos_df["fecha_fin"] = pd.to_datetime(datos_df["fecha_fin"])
    filas_nulas = obtener_muestra(datos_df, 0.08)
    filas_disponibles = datos_df.index.difference(filas_nulas)
    filas_antes = datos_df.loc[filas_disponibles].sample(frac=0.05, random_state=42).index
    datos_df.loc[filas_antes, "fecha_fin"] = (
        datos_df.loc[filas_antes, "fecha_fin"]
        - pd.to_timedelta([random.randint(1, 30) for _ in filas_antes], unit="d")
    )
    datos_df.loc[filas_nulas, "fecha_fin"] = pd.NaT
    datos_df["fecha_fin"] = datos_df["fecha_fin"].dt.strftime("%Y-%m-%d")

    # Estado: variantes 'en_curso', 'EN CURSO', ' Cerrado '
    filas_elegidas = obtener_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "estado"] = datos_df.loc[filas_elegidas, "estado"].map(escribir_mal)

    # 5% de las filas repetidas tal cual (duplicados exactos)
    filas_elegidas = obtener_muestra(datos_df, 0.05)
    duplicados = datos_df.loc[filas_elegidas]
    datos_df = pd.concat([datos_df, duplicados], ignore_index=True)

    return datos_df


def generar_retos(n=500):
    """Genera n retos, los ensucia y DEVUELVE el DataFrame."""
    random.seed(42)
    Faker.seed(42)
    df = pd.DataFrame(generar_datos(n))
    df = ensuciar(df)
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
