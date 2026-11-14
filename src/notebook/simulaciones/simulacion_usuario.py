'''
USR-F01 - Simular 400 filas de `usuarios` con Faker y ensuciarlas a proposito.

Actor que consulta, registra o participa en los retos. Con la libreria **Faker**
genera 400 filas falsas de la tabla `usuarios`, con las MISMAS columnas que usa
Backend II. Despues **ensucia los datos a proposito**: nulos, duplicados, espacios
sobrantes, mayusculas mezcladas y formatos distintos. Esos errores son los que se
arreglan en la etapa de limpieza.

Ejecutar desde la raiz del proyecto:
    python src/notebook/simulaciones/simulacion_usuario.py
'''

import random
import uuid

import pandas as pd
from faker import Faker

#1. Sembrar semillas para que el resultado sea siempre el mismo
random.seed(42)
Faker.seed(42)

#2. Datos a simular con su tipo de dato
# id (texto (UUID)),
# nombre (texto),
# correo (texto),
# contrasena_hash (texto),
# rol (texto),
# activo (booleano),
# fecha_registro (fecha y hora).

#3. Constantes
FILAS = 400
ROLES = ["Admin", "Empresa", "Participante"]
fake = Faker("es_CO")


#4. Funcion generadora
def generar_datos(numero_filas=FILAS):
    usuarios = []
    for _ in range(numero_filas):
        usuarios.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.name(),
            "correo": fake.email(),
            "contrasena_hash": fake.sha256(),
            "rol": random.choice(ROLES),
            "activo": random.choice([True, False]),
            "fecha_registro": fake.date_time_between(start_date="-2y", end_date="now"),
        })
    return usuarios


#5. Preparar la simulacion para ensuciar los datos

#5.1 Funcion para obtener una muestra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index


#5.2 Funcion auxiliar para escribir mal el rol ('admin', 'ADMIN', ' Empresa ', 'participante')
def escribir_mal(texto):
    variantes = [texto.lower(), texto.upper(), f" {texto} "]
    return random.choice(variantes)


#5.3 Funcion auxiliar para escribir el booleano como texto ('SI', 'No', '1', '0')
def convertir_booleano(valor):
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["No", "0"])


#5.4 Funcion principal para ensuciar los datos simulados
def ensuciar(datos_df):
    datos_df = datos_df.copy()

    #Nombre: el 10% con espacios sobrantes y el 8% en MAYUSCULAS
    filas_elegidas = obtener_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = "  " + datos_df.loc[filas_elegidas, "nombre"] + " "
    filas_elegidas = obtener_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "nombre"] = datos_df.loc[filas_elegidas, "nombre"].str.upper()

    #Correo: el 12% en MAYUSCULAS, el 5% sin la arroba y el 4% en None.
    #Cada error cae en filas distintas para que los porcentajes se cumplan.
    disponibles = datos_df.index
    mayusculas = datos_df.loc[disponibles].sample(frac=0.12, random_state=random.randint(0, 9999)).index
    disponibles = disponibles.drop(mayusculas)
    sin_arroba = datos_df.loc[disponibles].sample(n=round(len(datos_df) * 0.05), random_state=random.randint(0, 9999)).index
    disponibles = disponibles.drop(sin_arroba)
    nulos = datos_df.loc[disponibles].sample(n=round(len(datos_df) * 0.04), random_state=random.randint(0, 9999)).index
    disponibles = disponibles.drop(nulos)
    datos_df.loc[mayusculas, "correo"] = datos_df.loc[mayusculas, "correo"].str.upper()
    datos_df.loc[sin_arroba, "correo"] = datos_df.loc[sin_arroba, "correo"].str.replace("@", "")
    datos_df.loc[nulos, "correo"] = None

    #Correo: el 6% repite el correo de OTRO usuario (el back lo rechaza con 409).
    #Se copian correos validos sobre filas que no tenian ningun error de correo.
    destino = datos_df.loc[disponibles].sample(n=round(len(datos_df) * 0.06), random_state=random.randint(0, 9999)).index
    con_correo = datos_df.index.drop(nulos).drop(sin_arroba).drop(destino)
    origen = datos_df.loc[con_correo].sample(n=len(destino), random_state=random.randint(0, 9999)).index
    datos_df.loc[destino, "correo"] = datos_df.loc[origen, "correo"].values

    #Rol: variantes mal escritas
    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "rol"] = datos_df.loc[filas_elegidas, "rol"].map(escribir_mal)

    #Activo: a veces llega como texto ('SI', 'No', '1', '0')
    datos_df["activo"] = datos_df["activo"].astype(object)
    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "activo"] = datos_df.loc[filas_elegidas, "activo"].map(convertir_booleano)

    #Fecha: dos formatos mezclados
    #ISO    => 2026-03-15 14:30:00
    #LATINO => 15/03/2026 14:30
    iso = datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    datos_df["fecha_registro"] = iso
    filas_elegidas = obtener_muestra(datos_df, 0.25)
    datos_df.loc[filas_elegidas, "fecha_registro"] = latino.loc[filas_elegidas]

    #Duplicados exactos: el 5% de las filas es copia completa de otra fila (con su mismo id).
    #Va al final para que la copia salga con todos los errores ya puestos.
    filas_elegidas = obtener_muestra(datos_df, 0.05)
    filas_origen = datos_df.drop(filas_elegidas).sample(n=len(filas_elegidas), random_state=random.randint(0, 9999))
    datos_df.loc[filas_elegidas] = filas_origen.values

    return datos_df


#6. Funcion que arma todo y devuelve el DataFrame sucio (la importa exportacion_usuario.py)
def generar_usuarios(n=400):
    df = pd.DataFrame(generar_datos(n))
    df = ensuciar(df)
    return df


#7. Revisar los datos sucios (solo cuando se ejecuta este archivo directamente)
if __name__ == "__main__":
    df = generar_usuarios()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
