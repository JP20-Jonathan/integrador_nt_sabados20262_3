"""Punto de entrada general del proyecto integrador.
Ejecuta en orden el main de cada tabla (F01 + X01, L01, Q01 y G01).

Cada main se lanza como un proceso aparte para que sus rutas, argumentos
e imports no choquen entre si.

Ejecutar desde la raiz del proyecto, con el .venv activado:
    python main.py                    todas las tablas
    python main.py empresas retos     solo las tablas indicadas
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Orden pensado por dependencias: primero las tablas que otras referencian
MAINS = {
    "empresas": "main_empresa.py",
    "categorias": "main_categorias.py",
    "usuarios": "main_usuarios.py",
    "retos": "main_retos.py",
    "registros": "main_registros.py",
}


def titulo(texto):
    """Imprime un titulo para separar cada tabla en la consola."""
    print(f"\n{'#' * 60}\n{texto}\n{'#' * 60}", flush=True)


def ejecutar(tabla, script):
    """Ejecuta un main y devuelve True si termino sin errores."""
    titulo(f"Tabla {tabla} - {script}")
    inicio = time.time()
    resultado = subprocess.run([sys.executable, str(RAIZ / script)], cwd=RAIZ)
    print(f"\n{script} termino en {time.time() - inicio:.1f} s "
          f"(codigo {resultado.returncode})")
    return resultado.returncode == 0


def main():
    analizador = argparse.ArgumentParser(description="Ejecuta los main de todas las tablas.")
    analizador.add_argument("tablas", nargs="*",
                            help=f"tablas a ejecutar: {', '.join(MAINS)} (por defecto todas)")
    args = analizador.parse_args()
    desconocidas = [t for t in args.tablas if t not in MAINS]
    if desconocidas:
        analizador.error(f"tablas desconocidas: {', '.join(desconocidas)}")
    tablas = args.tablas or list(MAINS)

    estados = {tabla: ejecutar(tabla, MAINS[tabla]) for tabla in tablas}

    titulo("Resumen")
    for tabla, ok in estados.items():
        print(f"  {'PASA ' if ok else 'FALLA'}  {tabla}")
    sys.exit(0 if all(estados.values()) else 1)


if __name__ == "__main__":
    main()
