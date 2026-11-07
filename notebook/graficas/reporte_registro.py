"""
reporte_registro.py - HU G01: tres graficas con matplotlib y conclusiones de `registros`.

Ejecutar desde la raiz del proyecto:
    python notebook/graficas/reporte_registro.py
        lee data/limpio/registros_limpio.csv y guarda reportes/registros_grafica_N.png
        (si existe data/crudo/registros_sucio.csv, lo usa para contar las inscripciones
        duplicadas que la limpieza ya elimino)

Imprime al final las conclusiones.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")  # solo guarda imagenes, no abre ventanas
import matplotlib.pyplot as plt
import pandas as pd

RUTA_LIMPIO = "data/limpio/registros_limpio.csv"
RUTA_SUCIO = "data/crudo/registros_sucio.csv"
CARPETA = "reportes"
PAR = ["id_usuario", "id_reto"]


def grafica_1(conteo, carpeta):
    """Grafica 1: barras con las participaciones por estado."""
    plt.figure(figsize=(8, 5))
    conteo.plot(kind="bar")
    plt.title("Participaciones por estado")
    plt.xlabel("Estado")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=0)
    plt.tight_layout()
    ruta = f"{carpeta}/registros_grafica_1.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_2(por_mes, carpeta):
    """Grafica 2: linea con las participaciones por mes."""
    plt.figure(figsize=(9, 5))
    por_mes.plot(kind="line", marker="o")
    plt.title("Participaciones por mes")
    plt.xlabel("Mes")
    plt.ylabel("Número de participaciones")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    ruta = f"{carpeta}/registros_grafica_2.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_3(top_retos, carpeta):
    """Grafica 3: barras horizontales con los 10 retos con mas participantes."""
    plt.figure(figsize=(9, 5.5))
    top_retos.plot(kind="barh")
    plt.title("Los 10 retos con más participantes")
    plt.xlabel("Número de participantes")
    plt.ylabel("Reto (primeros 8 caracteres del id)")
    plt.gca().invert_yaxis()  # el reto con mas participantes arriba
    plt.tight_layout()
    ruta = f"{carpeta}/registros_grafica_3.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def contar_duplicadas(df_limpio, ruta_sucio):
    """Cuenta las inscripciones duplicadas (mismo usuario, mismo reto) y devuelve (total, copias exactas, origen)."""
    if ruta_sucio and os.path.isfile(ruta_sucio):
        crudo = pd.read_csv(ruta_sucio)
        total = int(crudo.duplicated(subset=PAR).sum())
        exactas = int(crudo.duplicated().sum())
        return total, exactas, "el archivo sucio"
    return int(df_limpio.duplicated(subset=PAR).sum()), 0, "el archivo limpio (la limpieza ya las eliminó)"


def conclusiones(df, conteo, por_mes, reto_top, participantes_top, duplicadas):
    """Imprime las conclusiones: reto mas popular, mes con mas inscripciones y duplicadas."""
    total, exactas, origen = duplicadas
    mes_top = por_mes.idxmax()
    estado_top = conteo.idxmax()
    print("\n===== CONCLUSIONES =====")
    print(f"1. El reto más popular es {reto_top}, con {participantes_top} participantes.")
    print(f"2. El mes con más inscripciones fue {mes_top}, con {int(por_mes.max())} participaciones.")
    print(f"3. El estado más frecuente es {estado_top}, con {int(conteo.max())} de {len(df)} participaciones.")
    if total:
        print(f"4. En {origen} se encontraron {total} inscripciones duplicadas "
              f"({exactas} copias exactas y {total - exactas} del mismo usuario en el mismo reto con otro id).")
    else:
        print(f"4. En {origen} se encontraron {total} inscripciones duplicadas.")
    print("   El back debe bloquearlas con 409 Conflict: un usuario no puede inscribirse dos veces en el mismo reto, "
          "y si el back las deja pasar, la tabla se llena de filas repetidas que inflan los conteos.")


def generar_reporte(ruta_limpio=RUTA_LIMPIO, ruta_sucio=RUTA_SUCIO, carpeta=CARPETA):
    """Lee el CSV limpio, guarda las tres graficas y imprime las conclusiones."""
    df = pd.read_csv(ruta_limpio)
    os.makedirs("reportes", exist_ok=True)
    os.makedirs(carpeta, exist_ok=True)

    #Las mismas consultas 3, 4 y 5 de la etapa Q01
    conteo = df["estado"].value_counts()
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    por_mes = df.groupby("mes")["id"].count()

    reto_top, participantes_top = top_retos.index[0], int(top_retos.iloc[0])
    top_retos.index = top_retos.index.str[:8]  # ids cortos para que se lean en la grafica

    rutas = [grafica_1(conteo, carpeta), grafica_2(por_mes, carpeta), grafica_3(top_retos, carpeta)]
    for ruta in rutas:
        print(f"-> guardada {ruta}")
    conclusiones(df, conteo, por_mes, reto_top, participantes_top, contar_duplicadas(df, ruta_sucio))
    return rutas


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    generar_reporte(*argumentos[:3])
