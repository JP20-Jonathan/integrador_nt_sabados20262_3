"""HU G01 - Graficas y conclusiones de la tabla retos.
Crea tres graficas (barras, linea e histograma), las guarda en reportes/
e imprime las conclusiones.
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # dibuja sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

# Rutas del proyecto (funcionan sin importar desde que carpeta se ejecute)
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]      # raiz del proyecto
RUTA_LIMPIO = RAIZ_PROYECTO / "data" / "limpio" / "retos_limpio.csv"
RUTA_SUCIO = RAIZ_PROYECTO / "data" / "crudo" / "retos_sucio.csv"
CARPETA_REPORTES = RAIZ_PROYECTO / "reportes"

COLOR_BARRAS = "#2a78d6"
COLOR_TEXTO = "#2b2b29"

RAZONES = {
    1: "es el inicio del año y la gente se pone propositos nuevos",
    2: "sigue el impulso de los propositos de inicio de año",
    3: "empieza el primer trimestre de trabajo y estudio ya con rutina",
    4: "coincide con la Semana Santa y el cambio de ritmo del año",
    5: "se aprovecha el arranque del segundo semestre de estudio",
    6: "se planea el descanso de mitad de año y se buscan nuevos habitos",
    7: "coincide con las vacaciones de mitad de año",
    8: "es el regreso a clases y a la rutina despues de vacaciones",
    9: "es un mes de rutina estable, ideal para empezar habitos",
    10: "empieza el ultimo trimestre y se busca cerrar el año con metas",
    11: "se preparan las metas de cierre de año",
    12: "se quiere cerrar el año con un ultimo reto antes de las fiestas",
}


def estilo_ejes(ax):
    """Deja los ejes discretos: sin bordes de arriba y derecha."""
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=COLOR_TEXTO)
    ax.title.set_color(COLOR_TEXTO)


def guardar_grafica(carpeta, numero):
    """Ajusta margenes, guarda la figura con dpi=120, la cierra y devuelve la ruta."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"retos_grafica_{numero}.png")
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1(df, carpeta):
    """Grafica 1 - barras: cantidad de retos por estado."""
    conteo = df["estado"].value_counts()
    plt.figure(figsize=(8, 5))
    ax = conteo.plot(kind="bar", color=COLOR_BARRAS, width=0.6, ax=plt.gca())
    ax.bar_label(ax.containers[0], padding=3, color=COLOR_TEXTO)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", color="#e5e4df", linewidth=0.8)
    ax.set_axisbelow(True)
    estilo_ejes(ax)
    plt.xticks(rotation=0)
    plt.title("Cantidad de retos por estado")
    plt.xlabel("Estado del reto")
    plt.ylabel("Cantidad de retos")
    return guardar_grafica(carpeta, 1), conteo


def serie_por_mes(df):
    """Cuenta los retos que empiezan cada mes, incluyendo meses sin retos (en 0)."""
    meses = df["fecha_inicio"].dropna().dt.to_period("M")
    por_mes = meses.value_counts().sort_index()
    todos = pd.period_range(por_mes.index.min(), por_mes.index.max(), freq="M")
    por_mes = por_mes.reindex(todos, fill_value=0)
    por_mes.index = por_mes.index.strftime("%Y-%m")
    return por_mes


def grafica_2(df, carpeta):
    """Grafica 2 - linea: retos que empiezan cada mes."""
    por_mes = serie_por_mes(df)
    plt.figure(figsize=(8, 5))
    ax = por_mes.plot(kind="line", marker="o", color=COLOR_BARRAS, linewidth=2, ax=plt.gca())
    estilo_ejes(ax)
    ax.grid(axis="y", color="#e5e4df", linewidth=0.8)
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45, ha="right")
    plt.title("Retos que empiezan cada mes")
    plt.xlabel("Mes de inicio (año-mes)")
    plt.ylabel("Cantidad de retos")
    return guardar_grafica(carpeta, 2), por_mes


def grafica_3(df, carpeta):
    """Grafica 3 - histograma: como se reparte la duracion de los retos."""
    plt.figure(figsize=(8, 5))
    ax = df["duracion_dias"].plot(
        kind="hist", bins=20, color=COLOR_BARRAS, edgecolor="white", ax=plt.gca()
    )
    estilo_ejes(ax)
    ax.grid(axis="y", color="#e5e4df", linewidth=0.8)
    ax.set_axisbelow(True)
    plt.title("Distribucion de la duracion de los retos")
    plt.xlabel("Duracion del reto (dias)")
    plt.ylabel("Cantidad de retos")
    return guardar_grafica(carpeta, 3)


def conclusiones(df, ruta_sucio, conteo, por_mes):
    """Imprime las conclusiones que pide la HU G01."""
    print(f"\n{'=' * 70}\nConclusiones\n{'=' * 70}")

    # 1. Filas eliminadas
    if ruta_sucio and os.path.isfile(ruta_sucio):
        sucio = pd.read_csv(ruta_sucio, encoding="utf-8")
        eliminadas = len(sucio) - len(df)
        print(f"1. Filas eliminadas: el archivo sucio tenia {len(sucio)} filas y el "
              f"limpio tiene {len(df)}, se eliminaron {eliminadas} (duplicados exactos).")
    else:
        print("1. Filas eliminadas: no encontre data/crudo/retos_sucio.csv para "
              "comparar. Ejecuta primero la exportacion (HU X01).")

    # 2. Mes con mas retos y posible razon
    mes_top = por_mes.idxmax()
    cantidad = int(por_mes.max())
    porcentaje = cantidad / por_mes.sum() * 100
    razon = RAZONES[int(mes_top.split("-")[1])]
    print(f"2. Los retos se concentran en {mes_top}: empiezan {cantidad} de "
          f"{int(por_mes.sum())} retos ({porcentaje:.0f}%). Puede ser porque {razon}.")

    # 3. Duracion promedio por estado
    validos = df[df["duracion_dias"] >= 0]
    promedio = validos.groupby("estado")["duracion_dias"].mean().round(1)
    detalle = ", ".join(f"{estado}: {dias} dias" for estado, dias in promedio.items())
    print(f"3. Duracion promedio por estado -> {detalle}.")

    # 4. Retos con fecha fin antes que inicio
    invertidos = int((df["duracion_dias"] < 0).sum())
    print(f"4. Retos con fecha fin antes que inicio: {invertidos} de {len(df)}. "
          "Dato para el back: hay que validar las fechas al guardar el reto.")

    # 5. Estado mas frecuente
    estado_top = conteo.index[0]
    print(f"5. El estado mas frecuente es '{estado_top}' con {int(conteo.iloc[0])} retos.")


def generar_reporte(ruta_limpio=RUTA_LIMPIO, ruta_sucio=RUTA_SUCIO):
    """Lee el archivo limpio, crea las tres graficas en reportes/, imprime
    las conclusiones y devuelve la lista de rutas de las imagenes."""
    df = pd.read_csv(ruta_limpio)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce")
    if "duracion_dias" not in df.columns:
        df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days

    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    ruta1, conteo = grafica_1(df, CARPETA_REPORTES)
    ruta2, por_mes = grafica_2(df, CARPETA_REPORTES)
    ruta3 = grafica_3(df, CARPETA_REPORTES)

    rutas = [Path(r) for r in (ruta1, ruta2, ruta3)]
    for ruta in rutas:
        print(f"Grafica guardada: {ruta.relative_to(RAIZ_PROYECTO)}")

    conclusiones(df, ruta_sucio, conteo, por_mes)
    return rutas


if __name__ == "__main__":
    generar_reporte()
