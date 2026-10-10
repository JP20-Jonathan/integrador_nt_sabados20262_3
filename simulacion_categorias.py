'''
Clasifica tematicamente los retos. Crea el script `src/simular_categorias.py`. Con la libreria **Faker** genera 250 filas falsas de la tabla `categorias`, con las MISMAS columnas que usa Backend II. Despues **ensucia los datos a proposito**: nulos, duplicados, espacios sobrantes, mayusculas mezcladas y formatos distintos. Esos errores son los que vas a arreglar en la etapa de limpieza, asi que tienen que quedar bien puestos.

'''
import random  # noqa: I001
import uuid

import pandas as pd
from faker import Faker


#1. Sembrar semillas para los datos a simular
random.seed(42)
Faker.seed(42)

#2. identificar los datos a simular con el tipo de dato

#id (texto (UUID)),
#nombre (texto),
#descripcion (texto),
#area_responsable (texto).

#3. Establecer las constantes para el numero de simulaciones
FILAS=250
#solo hay 10 categorias reales: en 250 filas el catalogo llega REPETIDO
CATEGORIAS=["Logistica","Tecnologia","Educacion","Salud","Medio Ambiente",
            "Innovacion","Finanzas","Mercadeo","Recursos Humanos","Energia"]
AREAS=["Operaciones","Sistemas","Academica","Bienestar","Gestion Ambiental"]
#version con tilde de cada categoria, para simular formatos distintos
TILDES={"Logistica":"Logística","Tecnologia":"Tecnología","Educacion":"Educación",
        "Innovacion":"Innovación","Energia":"Energía"}
fake=Faker("es_CO")

#4. Funcion generadora

def generar_categorias(numero_filas=FILAS):
    categorias=[]
    for _ in range(numero_filas):
        categorias.append({
            "id":str(uuid.uuid4()),
            "nombre":random.choice(CATEGORIAS),
            "descripcion":fake.sentence(nb_words=8),
            "area_responsable":random.choice(AREAS),
        })
    return categorias


#5 convirtiendo los datos generados en un dataframe con PANDAS
tabla_ordenada_categorias=pd.DataFrame(generar_categorias())


#6 provar la funcion
print(tabla_ordenada_categorias)


#7. preparar la simulacion para ensuciar mis datos

#7.1 funcion para obtener una mustra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0,9999)).index

#7.2 funcion auxiliar para cambiar valores de un texto
#ej: 'Logistica' => 'Logistica', 'LOGISTICA', ' logistica ', 'logística'
def escribir_mal(texto):
    variantes=[texto.title(),texto.upper(),f" {texto.lower()} ",TILDES.get(texto,texto).lower()]
    return random.choice(variantes)


#7.3 funcion principal para ensuciar los datos simulados
def ensuciar(datos_df):
    datos_df=datos_df.copy()

    #Nombre: el 30% llega con variantes del mismo nombre
    filas_elegidas=obtener_muestra(datos_df,0.3)
    datos_df.loc[filas_elegidas,"nombre"]=datos_df.loc[filas_elegidas,"nombre"].map(escribir_mal)

    #Descripcion: el 15% no deberia tener ningun valor, debe de estar en (None)
    filas_elegidas=obtener_muestra(datos_df,0.15)
    datos_df.loc[filas_elegidas,"descripcion"]=None

    #Area responsable: el 10% debe de estar en (None)
    filas_elegidas=obtener_muestra(datos_df,0.1)
    datos_df.loc[filas_elegidas,"area_responsable"]=None

    #Duplicados: el 8% de las filas se repite tal cual (duplicados exactos)
    filas_elegidas=obtener_muestra(datos_df,0.08)
    datos_df=pd.concat([datos_df,datos_df.loc[filas_elegidas]],ignore_index=True)

    return datos_df


#8 probar los datos sucios
tabla_sucia_categorias=ensuciar(tabla_ordenada_categorias)
print(tabla_sucia_categorias)
print(tabla_sucia_categorias.isna().sum())
print(tabla_sucia_categorias["nombre"].value_counts())
