'''
Tabla puente: vincula un Usuario con un Reto y deja trazabilidad.
Crea el script `src/simular_registros.py`. Con la libreria **Faker**
genera 800 filas falsas de la tabla `registros`, con las MISMAS columnas
que usa Backend II. Despues **ensucia los datos a proposito**: nulos, duplicados,
espacios sobrantes, mayusculas mezcladas y formatos distintos.
Esos errores son los que vas a arreglar en la etapa de limpieza,
asi que tienen que quedar bien puestos.
'''

import random
import uuid

import pandas as pd
from faker import Faker

#1. Sembrar semillas para los datos a simular
random.seed(42)

Faker.seed(42)

##2. Identificar los datos a simular con su tipo de dato

# id (texto (UUID)),
# fecha_registro (fecha y hora),
# observacion (texto),
# estado (texto),
# id_usuario (texto (UUID)),
# id_reto (texto (UUID)).


#3 Establecer una constante para el número de simulaciones

FILAS = 800
ESTADOS = ["Inscrito", "En proceso", "Finalizado"]
IDS_USUARIO = [str(uuid.uuid4()) for _ in range(400)]
IDS_RETO = [str(uuid.uuid4()) for _ in range(50)]
fake = Faker("es_CO")

#4 Función generadora
def generar_datos(numero_filas=FILAS):
    registros = []
    for _ in range(numero_filas):
        registros.append({
            "id": str(uuid.uuid4()),
            "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),
            "observacion": fake.sentence(nb_words=10),
            "estado": random.choice(ESTADOS),
            "id_usuario": random.choice(IDS_USUARIO),
            "id_reto": random.choice(IDS_RETO)
        })
    return registros


#5 Convirtiendo los datos generados en un dataframe con PANDAS
tabla_ordenada_registros = pd.DataFrame(generar_datos())


#6 Probar la función
print(tabla_ordenada_registros)


#7. Preparar la simulación para ensuciar mis datos

#7.1 Función para obtener una muestra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index

#7.2 Función Auxiliar para cambiar los valores de un texto
def escribir_mal(texto):
    variantes = [texto.lower(), texto.upper(), f" {texto} "]
    return random.choice(variantes)


#7.3 Función principal para ensuciar los datos simulados
def ensuciar(datos_df):
    datos_df = datos_df.copy()

    #Observacion: el 20% no debería tener ningún valor (None)
    filas_elegidas = obtener_muestra(datos_df, 0.2)
    datos_df.loc[filas_elegidas, "observacion"] = None

    #Estado: aplicar errores de escritura ('inscrito', 'EN PROCESO', ' Finalizado ')
    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "estado"] = datos_df.loc[filas_elegidas, "estado"].map(escribir_mal)

    #id_usuario + id_reto: el 10% repite el par de otra fila (el back lo prohibe con 409)
    filas_elegidas = obtener_muestra(datos_df, 0.1)
    filas_origen = datos_df.drop(filas_elegidas).sample(n=len(filas_elegidas), random_state=random.randint(0, 9999))
    datos_df.loc[filas_elegidas, ["id_usuario", "id_reto"]] = filas_origen[["id_usuario", "id_reto"]].values

    #Mezclar el formato de la fecha
    #ISO => YYYY-mm-dd HH:MM:SS
    #LATINO => dd/mm/YYYY HH:MM
    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    datos_df["fecha_registro"] = iso
    filas_elegidas = obtener_muestra(datos_df, 0.25)
    datos_df.loc[filas_elegidas, "fecha_registro"] = latino.loc[filas_elegidas]

    return datos_df


#8 Probar los datos sucios
tabla_sucia_registros = ensuciar(tabla_ordenada_registros)
print(tabla_sucia_registros)
