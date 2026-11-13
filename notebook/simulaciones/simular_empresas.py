import random
import uuid
import pandas as pd
from faker import Faker


#1. Sembrar semillas para los datos a simular
random.seed(42)
Faker.seed(42)

#Constantes
FILAS = 300
SECTORES = ["Tecnología", "Salud", "Educación", "Finanzas", "Manufactura", "Energía", "Transporte", "Turismo", "Alimentos y Bebidas", "Medios y Entretenimiento"]
fake = Faker("es_CO")


#7 Preparar la simulacion para ensuciar mis datos

#7.1 funcion para obtener una muestra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac = porcentaje, random_state = random.randint(0, 9999)).index

#7.1.1 Funcion para obtener origen y destino SIN filas en comun
def obtener_origen_destino(datos, porcentaje):
    filas_origen = obtener_muestra(datos, porcentaje)
    resto = datos.drop(index=filas_origen)
    filas_destino = resto.sample(n=len(filas_origen), random_state=random.randint(0, 9999)).index
    return filas_origen, filas_destino

#7.2 Funcion auxiliar para cambiar valores de un texto
def escribir_mal(texto):
    variantes  = [texto.upper(), f" {texto.lower()} "]
    return random.choice(variantes)

#7.3 Funcion auxiliar para cambiar los booleanos
def convertir_booleanos(valor):
    if valor:
        return random.choice(["SI", "1"])
    else:
        return random.choice(["No", "0"])

#7.4 Funcion auxiliar para el telefono: 3001234567 -> '300 123 4567' o '+57 300-123-4567'
def formatear_telefono(telefono):
    formatos = [
        telefono,
        f"{telefono[0:3]} {telefono[3:6]} {telefono[6:]}",
        f"+57 {telefono[0:3]}-{telefono[3:6]}-{telefono[6:]}",
    ]
    return random.choice(formatos)

#7.5 funcion principal para ensuciar los datos simulados
def ensuciar(datos_df):
    datos_df =  datos_df.copy()

    #nombre: 10% con espacios sobrantes al inicio y al final
    filas_elegidas = obtener_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = datos_df.loc[filas_elegidas, "nombre"].map(lambda nombre: f"  {nombre}  ")

    #nombre: 15% en MAYUSCULAS (de las filas que no tienen espacios)
    otras_filas = datos_df.drop(index=filas_elegidas)
    filas_elegidas = otras_filas.sample(n=round(len(datos_df) * 0.15), random_state=random.randint(0, 9999)).index
    datos_df.loc[filas_elegidas, "nombre"] = datos_df.loc[filas_elegidas, "nombre"].str.upper()

    #nit: la mitad con puntos y guiones (900.123.456-7) y la otra mitad sin nada (9001234567)
    filas_elegidas = obtener_muestra(datos_df, 0.5)
    otras_filas = datos_df.index.difference(filas_elegidas)
    datos_df.loc[filas_elegidas, "nit"] = datos_df.loc[filas_elegidas, "nit"].map(lambda nit: f"{nit[0:3]}.{nit[3:6]}.{nit[6:]}")
    datos_df.loc[otras_filas, "nit"] = datos_df.loc[otras_filas, "nit"].str.replace("-", "")

    #sector: variantes del mismo sector ('Salud', 'SALUD', ' salud ')
    filas_elegidas = obtener_muestra(datos_df, 0.1)
    datos_df.loc[filas_elegidas, "sector"] = datos_df.loc[filas_elegidas, "sector"].map(escribir_mal) #solo usamos el loc para los sub conjuntos

    #contacto: 8% no deberia tener ningun valor (none)
    filas_elegidas = obtener_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "contacto"] = None

    #Correo: 6% de los datos esten sin @
    filas_elegidas = obtener_muestra(datos_df, 0.06)
    datos_df.loc[filas_elegidas, "correo"] = datos_df.loc[filas_elegidas, "correo"].str.replace("@", "")

    #telefono: tres formatos mezclados
    datos_df["telefono"] = datos_df["telefono"].map(formatear_telefono)

    #activa: En ocasiones llega SI, No, 1 o 0
    datos_df["activa"] = datos_df["activa"].astype(object)
    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "activa"] = datos_df.loc[filas_elegidas, "activa"].map(convertir_booleanos)

    #nit: 3% de los nit repetidos entre empresas distintas
    filas_origen, filas_destino = obtener_origen_destino(datos_df, 0.03)
    datos_df.loc[filas_destino, "nit"] = datos_df.loc[filas_origen, "nit"].values

    #Tomar registros y copiarlos en otros registros para tener registros repetidos (5%)
    filas_origen, filas_destino = obtener_origen_destino(datos_df, 0.05)
    datos_df.loc[filas_destino] = datos_df.loc[filas_origen].values

    return datos_df


def generar_empresas(n=300):
    empresas = []
    for _ in range(n):
        empresas.append({
            "id":str(uuid.uuid4()),
            "nombre":fake.company(),
            "nit":fake.numerify("#########-#"),
            "sector":random.choice(SECTORES),
            "contacto":fake.name(),
            "correo":fake.company_email(),
            "telefono":fake.numerify("3#########"),
            "activa":random.choice([True, False]),
        })

    #convirtiendo los datos generados en un dataframe con PANDAS
    df = pd.DataFrame(empresas)
    df = ensuciar(df)
    return df


if __name__ == "__main__":
    df = generar_empresas(FILAS)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())