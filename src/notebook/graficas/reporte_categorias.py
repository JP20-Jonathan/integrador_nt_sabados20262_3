"""HU G01 - Graficas y conclusiones de la tabla categorias.
Crea las tres graficas de la HU (barras horizontales, torta y barras) y una
grafica de arana adicional, las guarda en reportes/ e imprime las conclusiones.
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # dibuja sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

# Rutas del proyecto (funcionan sin importar desde que carpeta se ejecute)
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]      # raiz del proyecto
RUTA_LIMPIO = RAIZ_PROYECTO / "data" / "limpio" / "categorias_limpio.csv"
RUTA_SUCIO = RAIZ_PROYECTO / "data" / "crudo" / "categorias_sucio.csv"
CARPETA_REPORTES = RAIZ_PROYECTO / "reportes"
CATEGORIAS_REALES = 10

# Colores: un solo color para las barras (una sola serie) y una paleta
# categórica en orden fijo para la torta; "Sin asignar" va en gris.
COLOR_BARRAS = "#2a78d6"
PALETA_AREAS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
                "#008300", "#6250d6", "#e34948"]
COLOR_SIN_ASIGNAR = "#9b9a94"
COLOR_TEXTO = "#2b2b29"
COLOR_ARANA = "#eb6834"
COLOR_REJILLA = "#8a8984"


def estilo_ejes(ax):
    """Deja los ejes discretos: sin bordes de arriba y derecha, texto gris oscuro."""
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=COLOR_TEXTO)
    ax.title.set_color(COLOR_TEXTO)


def guardar_grafica(carpeta, numero):
    """Ajusta márgenes, guarda la figura actual con dpi=120, la cierra
    y devuelve la ruta."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"categorias_grafica_{numero}.png")
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1(df, carpeta):
    """Gráfica 1 — barras horizontales: cuántas veces aparece cada categoría."""
    conteo = df["nombre"].value_counts().sort_values()  # la mayor queda arriba
    plt.figure(figsize=(8, 5))
    ax = conteo.plot(kind="barh", color=COLOR_BARRAS, width=0.7)
    ax.bar_label(ax.containers[0], padding=3, color=COLOR_TEXTO)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # conteos: solo enteros
    ax.grid(axis="x", color="#e5e4df", linewidth=0.8)
    ax.set_axisbelow(True)
    estilo_ejes(ax)
    plt.title("¿Cuántas veces aparece cada categoría?")
    plt.xlabel("Cantidad de filas")
    plt.ylabel("Categoría")
    return guardar_grafica(carpeta, 1), conteo.sort_values(ascending=False)


def grafica_2(df, carpeta):
    """Gráfica 2 — torta: reparto de las filas por área responsable."""
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    colores, i = [], 0
    for area in por_area.index:
        if area == "Sin asignar":
            colores.append(COLOR_SIN_ASIGNAR)
        else:
            colores.append(PALETA_AREAS[i % len(PALETA_AREAS)])
            i += 1
    plt.figure(figsize=(7, 6))
    ax = por_area.plot(kind="pie", autopct="%1.1f%%", colors=colores, startangle=90,
                       counterclock=False, pctdistance=0.75,
                       wedgeprops={"edgecolor": "white", "linewidth": 2},
                       textprops={"color": COLOR_TEXTO})
    ax.set_aspect("equal")
    plt.title("Reparto de categorías por área responsable")
    plt.xlabel("Porcentaje de filas de cada área")
    plt.ylabel("Área responsable")
    return guardar_grafica(carpeta, 2), por_area


def grafica_3(df, carpeta):
    """Gráfica 3 — barras: largo promedio de la descripción por categoría."""
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    plt.figure(figsize=(9, 5))
    ax = largos.plot(kind="bar", color=COLOR_BARRAS, width=0.7)
    ax.bar_label(ax.containers[0], padding=3, color=COLOR_TEXTO, fmt="%.1f")
    ax.set_ylim(0, largos.max() * 1.12)  # espacio para las etiquetas
    ax.grid(axis="y", color="#e5e4df", linewidth=0.8)
    ax.set_axisbelow(True)
    estilo_ejes(ax)
    plt.xticks(rotation=35, ha="right")
    plt.title("Largo promedio de la descripción por categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Caracteres en promedio")
    return guardar_grafica(carpeta, 3), largos


def grafica_4(df, carpeta):
    """Gráfica 4 — araña (radar): cuántas filas maneja cada área responsable.
    Cada eje es un área; mientras más lejos del centro, más filas tiene."""
    por_area = df.groupby("area_responsable")["id"].count().sort_index()
    etiquetas = list(por_area.index)
    valores = por_area.to_numpy(dtype=float)
    n = len(etiquetas)

    # Un ángulo por área, empezando arriba; se repite el primero para cerrar el polígono
    angulos = np.linspace(0, 2 * np.pi, n, endpoint=False)
    angulos_cerrados = np.append(angulos, angulos[0])
    valores_cerrados = np.append(valores, valores[0])

    plt.figure(figsize=(7, 7))
    ax = plt.subplot(polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Rejilla poligonal (en vez de círculos) y radios hacia cada vértice
    # Borde exterior en un número redondo por encima del máximo (múltiplo de 5)
    tope = int(np.ceil(valores.max() * 1.1 / 5) * 5)
    niveles = np.linspace(0, tope, 6)[1:]
    ax.grid(False)
    ax.spines["polar"].set_visible(False)
    for nivel in niveles:
        ax.plot(angulos_cerrados, [nivel] * (n + 1), color=COLOR_REJILLA, linewidth=1)
    for angulo in angulos:
        ax.plot([angulo, angulo], [0, tope], color=COLOR_REJILLA, linewidth=1)

    # Polígono de datos: relleno naranja semitransparente con borde y puntos
    ax.fill(angulos_cerrados, valores_cerrados, color=COLOR_ARANA, alpha=0.55, zorder=3)
    ax.plot(angulos_cerrados, valores_cerrados, color=COLOR_ARANA, linewidth=2, zorder=4)
    ax.scatter(angulos, valores, color=COLOR_ARANA, s=30, zorder=5)
    for angulo, valor in zip(angulos, valores):
        ax.annotate(f"{int(valor)}", (angulo, valor), xytext=(0, 8),
                    textcoords="offset points", ha="center", color=COLOR_TEXTO)

    ax.set_xticks(angulos)
    ax.set_xticklabels(etiquetas, color=COLOR_TEXTO)
    ax.tick_params(axis="x", pad=12)
    ax.set_yticklabels([])
    ax.set_ylim(0, tope)
    plt.title("Filas por área responsable (araña)", pad=24, color=COLOR_TEXTO)
    plt.xlabel("Área responsable", labelpad=18)
    plt.ylabel("Cantidad de filas", labelpad=34)
    return guardar_grafica(carpeta, 4), por_area


def conclusiones(df, ruta_sucio, conteo, por_area, largos):
    """Imprime las conclusiones que pide la HU G01 y lo que muestran las gráficas."""
    print(f"\n{'=' * 70}\nConclusiones\n{'=' * 70}")
    reales = df["nombre"].nunique()

    # 1. Filas eliminadas
    if ruta_sucio:
        sucio = pd.read_csv(ruta_sucio, encoding="utf-8")
        eliminadas = len(sucio) - len(df)
        nombres_sucios = sucio["nombre"].nunique()
        print(f"1. Filas eliminadas: el archivo sucio tenía {len(sucio)} filas y el "
              f"limpio tiene {len(df)}, así que se eliminaron {eliminadas} "
              f"(los duplicados exactos). Las variantes de escritura no borran filas: "
              f"se unificaron {nombres_sucios} formas de escribir el nombre en {reales}.")
    else:
        print("1. Filas eliminadas: no encontré data/crudo/categorias_sucio.csv para "
              "comparar. Ejecuta primero la exportación (HU X01).")

    # 2. Categorías reales
    estado = "como se esperaba" if reales == CATEGORIAS_REALES else \
        f"OJO: se esperaban {CATEGORIAS_REALES}, revisa la limpieza"
    print(f"2. Categorías reales: quedaron {reales} ({estado}).")

    # 3. Por qué `nombre` debe ser UNIQUE
    print("3. Por qué `nombre` debe ser UNICO en el back: el catálogo llegó con "
          "la misma categoría repetida y escrita de varias formas porque nada lo "
          "impedía. Si la base de datos declara `nombre` como UNIQUE (en Spring "
          "Boot, @Column(unique = true)), rechaza el segundo 'Logistica' en el "
          "momento de guardarlo y no hay que limpiarlo después. Ojo: UNIQUE "
          "compara el texto exacto, así que el back también debe normalizar el "
          "nombre antes de guardar (quitar espacios, unificar mayúsculas y "
          "tildes); si no, 'LOGISTICA' y 'Logistica' pasarían como distintas.")

    # Lo que muestran las gráficas
    print(f"4. Gráfica 1: la categoría que más se repite es {conteo.index[0]} "
          f"({conteo.iloc[0]} filas) y la que menos, {conteo.index[-1]} "
          f"({conteo.iloc[-1]}).")
    sin_asignar = int(por_area.get("Sin asignar", 0))
    print(f"5. Gráfica 2: el área con más filas es {por_area.index[0]} "
          f"({por_area.iloc[0]}); {sin_asignar} filas quedaron 'Sin asignar'.")
    print(f"6. Gráfica 3: {largos.index[0]} tiene las descripciones más largas "
          f"({largos.iloc[0]} caracteres en promedio) y {largos.index[-1]} las más "
          f"cortas ({largos.iloc[-1]}); las filas 'Sin descripcion' bajan el promedio.")
    reales_areas = por_area.drop("Sin asignar", errors="ignore")
    print(f"7. Gráfica 4 (araña): la carga entre áreas va de {reales_areas.min()} a "
          f"{reales_areas.max()} filas; mientras más parejo el polígono, más "
          f"equilibrado está el reparto. La punta más larga es {reales_areas.idxmax()}.")


def generar_reporte(ruta_limpio=RUTA_LIMPIO, ruta_sucio=RUTA_SUCIO):
    """Lee el archivo limpio, crea las cuatro graficas en reportes/, imprime
    las conclusiones y devuelve la lista de rutas de las imagenes."""
    df = pd.read_csv(ruta_limpio)
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    ruta1, conteo = grafica_1(df, CARPETA_REPORTES)
    ruta2, por_area = grafica_2(df, CARPETA_REPORTES)
    ruta3, largos = grafica_3(df, CARPETA_REPORTES)
    ruta4, _ = grafica_4(df, CARPETA_REPORTES)
    rutas = [Path(r) for r in (ruta1, ruta2, ruta3, ruta4)]
    for ruta in rutas:
        print(f"Grafica guardada: {ruta.relative_to(RAIZ_PROYECTO)}")

    sucio = ruta_sucio if os.path.isfile(ruta_sucio) else None
    conclusiones(df, sucio, conteo, por_area, largos)
    return rutas


if __name__ == "__main__":
    generar_reporte()