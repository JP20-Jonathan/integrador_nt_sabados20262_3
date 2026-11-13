# integrador_nt_sabados20262_3
Proyecto integerador nuevas tecnologias


## Estructura del proyecto

Cada tabla tiene un script por etapa, todos con el mismo patrón de nombre (`<etapa>_<tabla>.py`),
y un main propio que ejecuta solo esa tabla.

```
main_usuarios.py              <- main de cada tabla (main_<tabla>s.py)
main_registros.py
requirements.txt
src/notebook/
  simulaciones/   simulacion_<tabla>.py    F01: Faker + ensuciar   -> generar_<tabla>s(n) devuelve el DataFrame
  exportacion/    exportacion_<tabla>.py   X01: csv, xlsx y json   -> data/crudo/<tabla>s_sucio.*
  limpieza/       limpieza_<tabla>.py      L01: limpiar con pandas -> data/limpio/<tabla>s_limpio.csv
  consultas/      consulta_<tabla>.py      Q01: 5 consultas        -> data/limpio/<tabla>s_consulta_N.csv
  graficas/       reporte_<tabla>.py       G01: 3 gráficas         -> reportes/<tabla>s_grafica_N.png
data/             (no se sube: se genera con el main)
reportes/         (sí se sube: las gráficas de cada tabla)
```

| Tabla | Estado |
|---|---|
| usuarios | `main_usuarios.py` + 5 scripts |
| registros | `main_registros.py` + 5 scripts |
| retos, empresas, categorias | solo `simulacion_<tabla>.py` (pendiente) |


## Cómo agregar tu tabla

1. Crea tu rama desde `develop`: `git switch -c feature/pipeline_<tabla> develop`.
2. Crea tus 5 scripts en las carpetas de `src/notebook/` con el nombre `<etapa>_<tabla>.py`.
   Usa como ejemplo los de `usuario` o `registro`.
3. Usa las rutas de las HU, relativas a la raíz: `data/crudo/`, `data/limpio/` y `reportes/`.
   Nombra tus archivos con el nombre de tu tabla (`retos_sucio.csv`, `retos_grafica_1.png`...)
   para no pisar los de los demás.
4. Copia `main_usuarios.py` como `main_<tabla>s.py` y cambia los imports por los de tu tabla.
5. Si necesitas una librería nueva, **agrega** su línea a `requirements.txt` (no lo reemplaces).
6. Si usas skills de revisión en la raíz, agrega sus carpetas a `.gitignore` (no se suben).
7. Sube tu código y tus gráficas de `reportes/`, y abre el PR hacia `develop`.


## Cómo generar los datos

La carpeta `data/` no se sube al repositorio (está en `.gitignore`): se genera ejecutando el main de cada tabla
desde la raíz del proyecto, con el entorno activado.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python main_usuarios.py     # tabla usuarios
python main_registros.py    # tabla registros
```

Cada main acepta `--fase N` (1 simular y exportar, 2 limpiar, 3 consultas, 4 gráficas) para ejecutar una sola fase.
Los archivos generados se reemplazan en cada ejecución.
