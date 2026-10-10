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

#3 ESTABLECER UNA CONSTANTE PARA EL NUMERO DE SIMULACIONES
FILAS=400
ROLES=["administrador","empresario","estudiante","profesor"]
falsito=Faker("es_CO")

#4. Funcion generadora

def generar_datos(numero_filas=FILAS):
    usuarios=[]
    for _ in range (numero_filas):
        usuarios.append({
            "id":str(uuid.uuid4()),
            "nombre":falsito.name(),
            "correo":falsito.email(),
            "contraseña_hash":falsito.sha256(),
            "activo":random.choice([True,False]),
            "rol":random.choice(ROLES),
            "fecha_registro":falsito.date_time_between(start_date="-2y", end_date="now")
        })
    return usuarios


#5 convirtiendo los datos generados en un dataframe con PANDAS
tabla_ordenada_usuarios=pd.DataFrame(generar_datos())


#6 provar la funcion
print(tabla_ordenada_usuarios)


#7. preparar la simulacion para ensuciar mis datos
 
#7.1 funcion para obtener una mustra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0,9999)).index

#7.2 funcion auxiliar para cambiar valores de un texto  
def escribir_mal(texto):
    variantes=[texto.lower(),texto.title(), texto.capitalaize(),f" {texto} ","Andres"]
    return random.choice(variantes)

#7.3 funcion paraa cambiar los booleanos 
def convertir_booleano(valor):
    if valor:
        return random.choice(["SI","1"])
    else:
        return random.choice(["NO","0"])


#7.4 funcion principal para ensuciar los datos simulados     
def ensuciar(datos_df):
    datos_df=datos_df.copy()

    #Nombre: el 10% tenga espacion y el 8 % este en mayusculas
    filas_elegidas=obtener_muestra(datos_df,0.1) 
    datos_df.loc[filas_elegidas,"nombre"]=" "+datos_df.loc[filas_elegidas,"nombre"]+" "
       
    filas_elegidas=obtener_muestra(datos_df,0.08)
    datos_df.loc[filas_elegidas,"nombre"]=datos_df.loc[filas_elegidas,"nombre"].str.upper()

    #correo: el 5% de los datos este sin @
    filas_elegidas=obtener_muestra(datos_df,0.05)
    datos_df.loc[filas_elegidas,"correo"]=datos_df.loc[filas_elegidas,"correo"].str.replace("@","")

    #Correo: el 4 % de los correos no debererian tener ningun valor, debe de estar en (NOne)
    filas_elegidas=obtener_muestra(datos_df,0.04)
    datos_df.loc[filas_elegidas,"correo"]=None     

    #Rol: aplicar errores de escritura (variantes)
    filas_elegidas=obtener_muestra(datos_df,0.1)
    datos_df.loc[filas_elegidas,"rol"]=datos_df.loc[filas_elegidas,"rol"].map(escribir_mal)

    #Activo: en ocaciones llega SI, NO, 1, 0
    datos_df["activo"]=datos_df["activo"].astype(object) 
    filas_elegidas=obtener_muestra(datos_df,0.15)
    datos_df.loc[filas_elegidas,"activo"]=datos_df.loc[filas_elegidas,"activo"].map
    (convertir_booleano)  # noqa: B018
  
    #Mezclar el formato de las fechas 
    #ISO=> 2026/10/03 YYY/mm/dd HH:MM:SS
    #LATINO=>03/10/2026  d/m/y h/M

    iso=datos_df["fechas_registro"].dt.strtime("%Y-%m-%d %H:%M:%S")
    latino=datos_df["fechas_registro"].dt.strtime("%d/%m/%y %H:%M")
    datos_df["fechas_registro"]=iso
    filas_elegidas=obtener_muestra(datos_df,0.25)
    datos_df.loc[filas_elegidas,"fecha_registro"]=latino.loc[filas_elegidas] 
    