"""
reporte_usuario.py - USR-G01: tres graficas con matplotlib y conclusiones de `usuarios`.

Ejecutar desde la raiz del proyecto:
    python src/notebook/graficas/reporte_usuario.py
        lee data/limpio/usuarios_limpio.csv y guarda reportes/usuarios_grafica_N.png
        (si existe data/crudo/usuarios_sucio.csv, lo usa para contar los correos
        repetidos e invalidos que llegaron antes de limpiar)

Imprime al final las conclusiones.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")  # solo guarda imagenes, no abre ventanas
import matplotlib.pyplot as plt
import pandas as pd

RUTA_LIMPIO = "data/limpio/usuarios_limpio.csv"
RUTA_SUCIO = "data/crudo/usuarios_sucio.csv"
CARPETA = "reportes"


def grafica_1(df, carpeta):
    """Grafica 1: barras con la cantidad de usuarios por rol."""
    plt.figure(figsize=(8, 5))
    df["rol"].value_counts().plot(kind="bar")
    plt.title("Usuarios por rol")
    plt.xlabel("Rol")
    plt.ylabel("Número de usuarios")
    plt.xticks(rotation=0)
    plt.tight_layout()
    ruta = f"{carpeta}/usuarios_grafica_1.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_2(por_mes, carpeta):
    """Grafica 2: linea con los usuarios registrados por mes."""
    plt.figure(figsize=(11, 5))
    por_mes.plot(kind="line", marker="o")
    plt.title("Usuarios registrados por mes")
    plt.xlabel("Mes")
    plt.ylabel("Número de usuarios")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    ruta = f"{carpeta}/usuarios_grafica_2.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_3(tabla, carpeta):
    """Grafica 3: barras apiladas con activos e inactivos por rol."""
    tabla = tabla.rename(columns={True: "Activo", False: "Inactivo"})
    tabla.plot(kind="bar", stacked=True)
    plt.gcf().set_size_inches(9, 5)
    plt.title("Usuarios activos e inactivos por rol")
    plt.xlabel("Rol")
    plt.ylabel("Número de usuarios")
    plt.xticks(rotation=0)
    plt.legend(title="Estado", loc="upper left", bbox_to_anchor=(1.01, 1))  # fuera de las barras
    plt.tight_layout()
    ruta = f"{carpeta}/usuarios_grafica_3.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def contar_correos(df_limpio, ruta_sucio):
    """Devuelve (repetidos, invalidos, origen): correos repetidos entre usuarios y correos sin @."""
    if ruta_sucio and os.path.isfile(ruta_sucio):
        crudo = pd.read_csv(ruta_sucio).drop_duplicates()
        correos = crudo["correo"].dropna().str.strip().str.lower()
        return int(correos.duplicated().sum()), int((~correos.str.contains("@")).sum()), "el archivo sucio"
    invalidos = int((~df_limpio["correo_valido"]).sum())
    return 0, invalidos, "el archivo limpio (la limpieza ya quitó los repetidos)"


def conclusiones(df, tabla, por_mes, correos):
    """Imprime las conclusiones: rol que predomina, % de inactivos y correos repetidos o invalidos."""
    repetidos, invalidos, origen = correos
    conteo = df["rol"].value_counts()
    inactivos = int((df["activo"] == False).sum())  # noqa: E712
    pct_inactivos = inactivos / len(df) * 100
    print("\n===== CONCLUSIONES =====")
    print(f"1. El rol que predomina es {conteo.idxmax()}, con {int(conteo.max())} de {len(df)} usuarios "
          f"({conteo.max() / len(df) * 100:.1f}%).")
    print(f"2. El {pct_inactivos:.1f}% de los usuarios está inactivo ({inactivos} de {len(df)}). "
          "Son cuentas que existen pero no participan: la plataforma debe trabajar en reactivarlas, "
          "y los conteos de usuarios deberían filtrar solo los activos para no inflar las cifras.")
    print(f"3. El mes con más registros fue {por_mes.idxmax()}, con {int(por_mes.max())} usuarios.")
    print(f"4. En {origen} aparecieron {repetidos} correos repetidos y {invalidos} correos inválidos (sin @).")
    print("   El back debe declarar `correo` como UNICO y responder 409 Conflict si ya existe: el correo "
          "identifica al usuario para iniciar sesión, y si se repite no se sabe a qué cuenta pertenece. "
          "Además debe validar el formato del correo antes de guardarlo.")


def generar_reporte_usuarios(ruta_limpio=RUTA_LIMPIO, ruta_sucio=RUTA_SUCIO, carpeta=CARPETA):
    """Lee el CSV limpio, guarda las tres graficas y imprime las conclusiones."""
    df = pd.read_csv(ruta_limpio)
    os.makedirs("reportes", exist_ok=True)
    os.makedirs(carpeta, exist_ok=True)

    #Las mismas consultas 4 y 5 de la etapa Q01
    tabla = df.groupby(["rol", "activo"])["id"].count().unstack(fill_value=0)
    por_mes = df.groupby("mes")["id"].count()

    rutas = [grafica_1(df, carpeta), grafica_2(por_mes, carpeta), grafica_3(tabla, carpeta)]
    for ruta in rutas:
        print(f"-> guardada {ruta}")
    conclusiones(df, tabla, por_mes, contar_correos(df, ruta_sucio))
    return rutas


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    generar_reporte_usuarios(*argumentos[:3])
