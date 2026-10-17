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

#7.1 funcion para optener una muestra de los datos
def obtener_muestra(datos, porcentaje):
    return datos.sample(frac = porcentaje, random_state = random.randint(0, 9999)).index

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

#7.4 funcion principal para ensuciar los datos simulados
def ensuciar(datos_df):
    datos_df =  datos_df.copy()

    #nit: la mitad con puntos y guiones (900.123.456-7) y la otra mitad sin nada (9001234567)
    filas_elegidas = obtener_muestra(datos_df, 0.5)
    otras_filas = datos_df.index.difference(filas_elegidas)
    datos_df.loc[filas_elegidas, "nit"] = datos_df.loc[filas_elegidas, "nit"].map(lambda nit: f"{nit[0:3]}.{nit[3:6]}.{nit[6:]}")
    datos_df.loc[otras_filas, "nit"] = datos_df.loc[otras_filas, "nit"].str.replace("-", "")

    filas_elegidas = obtener_muestra(datos_df, 0.1)
    datos_df.loc[filas_elegidas, "sector"] = datos_df.loc[filas_elegidas, "sector"].map(escribir_mal) #solo usamo el loc para los sub conjutos

    #contacto: 8% no deberia tener ningun valor (none)
    filas_elegidas = obtener_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "contacto"] = None

    #Correo: 6% de los datos esten sin @
    filas_elegidas = obtener_muestra(datos_df, 0.06)
    datos_df.loc[filas_elegidas, "correo"] = datos_df.loc[filas_elegidas, "correo"].str.replace("@", "")

    #activa: En ocaciones llega SI, No, 1 o 0
    datos_df["activa"] = datos_df["activa"].astype(object)
    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "activa"] = datos_df.loc[filas_elegidas, "activa"].map(convertir_booleanos)

    #nit: 3% de los nit repetidos entre empresas distintas
    filas_origen = obtener_muestra(datos_df, 0.03)
    filas_destino = obtener_muestra(datos_df, 0.03)
    datos_df.loc[filas_destino, "nit"] = datos_df.loc[filas_origen, "nit"].values

    #Tomar registros y copiarlos en otros registros para tener registros repetidos (5%)
    filas_origen = obtener_muestra(datos_df, 0.05)
    filas_destino = obtener_muestra(datos_df, 0.05)
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
