from pathlib import Path

#1 Configuración de las rutas
NOMBRE_ENTIDAD = "usuario"
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
# print(f"oeeee: {CARPETA_PROYECTO}")
CARPETA_CRUDOS = CARPETA_PROYECTO/"datos"/"crudos"
CARPETA_LIMPIOS = CARPETA_PROYECTO/"datos"/"limpios"
CARPETA_PRODUCTOS = CARPETA_PROYECTO/"datos"/"reportes"

# Funciones genericas para crear los archivos (ojo se necesita el DF)

def preparar_carpeta(carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta

def exportar_csv(datos_df_sucio,carpeta,nombre_archivo):
    ruta = preparar_carpeta(carpeta)/f"{nombre_archivo}.csv"
    datos_df_sucio.to_csv(ruta, sep=";")
    return ruta

def exportar_json(datos_df_sucio,carpeta,nombre_archivo):
    ruta = preparar_carpeta(carpeta)/f"{nombre_archivo}.json"
    datos_df_sucio.to_json(ruta,orient="records", ident="2")
    return ruta

def exportar_excel(datos_df_sucio,carpeta,nombre_archivo):
    ruta=preparar_carpeta(carpeta)/f"{nombre_archivo}.xlsx"
    datos_df_sucio.to_excel(ruta,engine="openpyxl")
    return ruta


#3 Llamamos las funciones para crear los archivos
def exportar_usuarios(datos_df_sucio):
    return [
        exportar_csv(datos_df_sucio,CARPETA_CRUDOS,f"{NOMBRE_ENTIDAD}_crudo"),
        exportar_csv(datos_df_sucio,CARPETA_CRUDOS,f"{NOMBRE_ENTIDAD}_crudo"),
        exportar_csv(datos_df_sucio,CARPETA_CRUDOS,f"{NOMBRE_ENTIDAD}_crudo")
            ]