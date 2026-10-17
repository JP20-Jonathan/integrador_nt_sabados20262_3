'''
El elemento central: la necesidad que publica la empresa. Crea el script 
`src/simular_retos.py`. Con la libreria **Faker** genera 500 filas falsas 
de la tabla `retos`, con las MISMAS columnas que usa Backend II. Despues
**ensucia los datos a proposito**: nulos, duplicados, espacios sobrantes, 
mayusculas mezcladas y formatos distintos. Esos errores son los que vas a
arreglar en la etapa de limpieza, asi que tienen que quedar bien puestos.

Usa `Faker("es_CO")` y fija la semilla con `Faker.seed(42)` y `random.seed(42)`
para que el resultado sea SIEMPRE el mismo y tu compañero pueda reproducirlo.
'''

import random
import uuid
import pandas as pd
from faker import Faker 
from datetime import date, timedelta

#1. Sembrar semillas para los datos a simular

random.seed(42)
Faker.seed(42)

#2. Identificar los datos a simluar con su tipo de dato.

'''
id (texto (UUID))
nombre (texto)
descripcion (texto)
fecha_inicio (fecha)
fecha_fin (fecha)
estado (texto) *******
id_empresa (texto (UUID))
id_categoria (texto (UUID))
id_prioridad (texto (UUID)).
'''

#3. Establecer una constante para el numero de simulaciones
FILAS = 500
ESTADOS = ["Abierto", "Cerrado", "En progreso", "Pendiente"]
IDS_EMPRESA =[str(uuid.uuid4()) for _ in range(10)]
IDS_CATEGORIA = [str(uuid.uuid4()) for _ in range(5)]
IDS_PRIORIDAD = [str(uuid.uuid4()) for _ in range(3)]
FALSITO = Faker("es_CO")
FECHA_INICIO = date.today()

#4 Funcion generadora
def generar_datos(numero_filas = 500):
    retos = []
    for _ in range(numero_filas):
        retos.append({
            "id": str(uuid.uuid4()),
            "nombre": FALSITO.sentence(nb_words=6).rstrip("."),
            "descripcion": FALSITO.sentence(nb_words=12),
            "fecha_inicio": FALSITO.date_between(start_date="-1y", end_date="+3m"),
            "fecha_fin":FECHA_INICIO + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD)

        })
    return retos


tabla_ordenada_retos = pd.DataFrame(generar_datos())

print(tabla_ordenada_retos)

#7. Preparar la simulacion para ensuciar mis datos

#7.1 Funcion para obtener una muestra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint
    (0,9999)).index;

#7.2 Funición auxilliar para cambiar valores de un texto
def escribir_mal(texto):
    variantes=[texto.lower(),texto.title(),texto.
    capitalize(),f" {texto} ", "Andres"]
    return random.choice(variantes)

#7.3 Funcion Auxiliar para cambiar los booleanos
def convertir_booleano(valor):
    if valor :
        return random.choice(["SÍ", "1"])
    else:
        return random.choice(["NO", "0"])

#7.4 Función principal para ensuciar los datos simulados
def ensuciar (datos_df):
    datos_df=datos_df.copy()

    #Nombre: el 10% tenga espacios
    filas_elegidas = obtener_muestra(datos_df, 0.1)
    datos_df.loc[filas_elegidas, "nombre"]=" "+datos_df.loc[filas_elegidas,"nombre"]+" "

    #Descripción : el 12% en None (nulos)
    filas_elegidas = obtener_muestra(datos_df, 0.12)
    datos_df.loc[filas_elegidas, "descripcion"]=None

    #Fecha_inicio : dos formatos mezclados: "2026-03-02" y "02/03/2026".
    #Primero, convierto la columna a un tipo de fecha que Pandas pueda manejar
    datos_df["fecha_inicio"] = pd.to_datetime(
        datos_df["fecha_inicio"]
    )

    iso = datos_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino = datos_df["fecha_inicio"].dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = iso
    filas_elegidas = obtener_muestra(datos_df, 0.25)
    datos_df.loc[filas_elegidas, "fecha_inicio"] = latino.loc[filas_elegidas]

    #Fecha_fin : 8% en None y 5% ANTERIOR a fecha_inicio (error logico a detectar).
    filas_nulas = obtener_muestra(datos_df, 0.08)
    datos_df.loc[filas_nulas, "fecha_fin"]=None
    filas_disponibles = datos_df.index.difference(filas_nulas)
    filas_elegidas = datos_df.loc[filas_disponibles].sample( # revisar profe
        frac=0.05,
        random_state=42
    ).index
    datos_df.loc[filas_elegidas, "fecha_fin"] = (
        datos_df.loc[filas_elegidas, "fecha_inicio"]
        - pd.to_timedelta(
            [random.randint(1, 30) for _ in filas_elegidas],
            unit="d"
        )
    )

    #Estado: variantes: 'en_curso', 'EN CURSO', ' Cerrado '.
    filas_elegidas = obtener_muestra(datos_df, 0.1)
    datos_df.loc[filas_elegidas, "estado"] = datos_df.loc[filas_elegidas, "estado"].map(escribir_mal)

    #5% de las filas repetidas tal cual (duplicados exactos).
    filas_elegidas = obtener_muestra(datos_df, 0.05)
    duplicados = datos_df.loc[filas_elegidas]
    datos_df = pd.concat([datos_df, duplicados], ignore_index=True)
    
