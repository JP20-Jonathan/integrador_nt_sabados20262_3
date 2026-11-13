"""HU G01 - Gráficas y conclusiones de la tabla empresas.

Lee   data/limpio/empresas_limpio.csv
Guarda reportes/empresas_grafica_1.png, _2.png y _3.png

Se puede ejecutar solo (desde la raíz del proyecto):
    python notebook/graficas/graficar_empresas.py
o desde main_empresa.py:
    python main_empresa.py
"""

import os

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

# Rutas: este archivo está en <raiz>/notebook/graficas/
CARPETA_GRAFICAS = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(CARPETA_GRAFICAS))

RUTA_LIMPIO = os.path.join(RAIZ_PROYECTO, "data", "limpio", "empresas_limpio.csv")
CARPETA_REPORTES = os.path.join(RAIZ_PROYECTO, "reportes")

VERDE = "#55A868"
ROJO = "#C44E52"
AZUL = "#4C72B0"


def leer_limpio():
    """Lee el CSV limpio. nit y telefono como texto para no perder ceros a la izquierda."""
    df = pd.read_csv(RUTA_LIMPIO, dtype={"nit": str, "telefono": str}, encoding="utf-8")
    if df["activa"].dtype != bool:
        df["activa"] = df["activa"].astype(str).str.strip().str.upper().map({"TRUE": True, "FALSE": False})
    return df


def guardar_grafica(nombre_archivo):
    """Ajusta el diseño, guarda la figura en reportes/ con dpi=120 y la cierra."""
    ruta = os.path.join(CARPETA_REPORTES, nombre_archivo)
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    print("Gráfica guardada:", os.path.relpath(ruta, RAIZ_PROYECTO))


def grafica_1_por_sector(df):
    """Gráfica 1 - Barras: cantidad de empresas por sector."""
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    por_sector.plot(kind="bar", color=AZUL)
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    guardar_grafica("empresas_grafica_1.png")


def grafica_2_activas_inactivas(df):
    """Gráfica 2 - Torta: empresas activas vs inactivas."""
    estado = df["activa"].map({True: "Activa", False: "Inactiva"})
    plt.figure(figsize=(6, 6))
    # Orden fijo para que Activa siempre sea verde e Inactiva roja.
    conteo = estado.value_counts().reindex(["Activa", "Inactiva"], fill_value=0)
    conteo.plot(kind="pie", autopct="%1.1f%%", colors=[VERDE, ROJO], startangle=90)
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Estado de la empresa")
    plt.ylabel("")  # la torta no usa eje Y; vacío para que no salga 'count'
    guardar_grafica("empresas_grafica_2.png")


def grafica_3_apilada_por_sector(df):
    """Gráfica 3 - Barras apiladas: activas e inactivas por sector."""
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    tabla = tabla.rename(columns={True: "Activa", False: "Inactiva"})[["Activa", "Inactiva"]]
    tabla = tabla.loc[tabla.sum(axis=1).sort_values(ascending=False).index]
    tabla.plot(kind="bar", stacked=True, color=[VERDE, ROJO], figsize=(8, 5))
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Estado")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    guardar_grafica("empresas_grafica_3.png")


def imprimir_conclusiones(df):
    """Responde las preguntas de la HU: sector líder, % inactivo y correos inválidos."""
    total = len(df)
    por_sector = df["sector"].value_counts()
    maximo = por_sector.max()
    lideres = por_sector[por_sector == maximo].index.tolist()

    inactivas = int((~df["activa"]).sum())
    pct_inactivas = inactivas / total * 100

    invalidos = df[~df["correo"].astype(str).str.contains("@")]

    print("\n=== CONCLUSIONES ===")
    print(f"Total de empresas analizadas: {total}")

    if len(lideres) == 1:
        print(f"1. El sector con más empresas registradas es '{lideres[0]}' "
              f"con {maximo} empresas ({maximo / total * 100:.1f}% del total).")
    else:
        print(f"1. Hay empate entre los sectores {', '.join(lideres)} con {maximo} empresas cada uno.")

    print(f"2. El {pct_inactivas:.1f}% de las empresas está inactivo ({inactivas} de {total}).")
    if pct_inactivas >= 30:
        print("   Es un porcentaje alto: la plataforma tiene muchas empresas que no publican ni "
              "contratan; conviene contactarlas para reactivarlas o depurar las que ya no operan.")
    else:
        print("   La mayoría está activa, pero conviene hacer seguimiento a las inactivas para reactivarlas.")

    print(f"3. Aparecieron {len(invalidos)} correos inválidos "
          f"(ejemplos: {', '.join(invalidos['correo'].head(3))}).")
    print("   Hay que validarlos en el back porque la validación del front se puede saltar "
          "(peticiones directas a la API, importaciones masivas); un correo inválido impide "
          "contactar a la empresa y ensucia los datos.")


def graficar_empresas():
    """Crea la carpeta reportes/, genera las tres gráficas e imprime las conclusiones."""
    df = leer_limpio()
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    grafica_1_por_sector(df)
    grafica_2_activas_inactivas(df)
    grafica_3_apilada_por_sector(df)
    imprimir_conclusiones(df)


if __name__ == "__main__":
    graficar_empresas()