# Hallazgos — Parte A

**Grupo:**  1  · **Integrantes:**  Kevin Leonardo Chaparro Reyes, Valentina Muñoz Palma, Paula Margarita Triana Ancinez

> No borren la fila de ejemplo hasta haber comprobado que su tabla se parsea
> (`python verificar_entrega.py`). El formato es rígido: ocho columnas, en este
> orden. Una tabla torcida se rechaza indicando la línea, no se «entiende igual».
>
> **Tuberías dentro de una celda:** si su comando lleva `|` —y varios lo llevarán,
> por `grep`, `head` o `jq`— escríbanlo `\|`. Sin escapar, Markdown lo lee como
> separador de columna y su fila pasa a tener nueve.

| ID | Síntoma observable | Causa | Módulo · Sección | SHA donde se observa | Comando de evidencia | Salida obtenida | Corrección aplicada |
|----|--------------------|-------|------------------|----------------------|----------------------|-----------------|---------------------|
| H1 | `requirements.txt` no fija versiones | Las dependencias se listan sin `==` | M1 · 3. Entornos virtuales: venv frente a conda | `requirements.txt` | `cat requirements.txt` | ` fastapi ` <br><br> ` uvicorn ` <br><br> ` sqlalchemy ` <br><br> ` pydantic ` <br><br> ` scikit-learn ` <br><br> ` numpy ` <br><br> ` pytest ` <br><br> ` httpx` | `python -m pip freeze > requirements.txt` luego de correr todo el  repositorio para no tener que hacer mas actualizaciones de el |
| H2 | `.gitignore` solo ignora `*.pyc` | No cubre `.env`, `*.db`, `.venv`, `__pycache__/` | M1 · 3. Entornos virtuales: venv frente a conda | `.gitignore` | `cat .gitignore` | `*.pyc` | Añadir reglas para `.env`, `*.db`, `.venv`, `__pycache__`, etc. |
| H3 | `app.db` esta versionado en el repositorio | La base de datos SQLite se commiteó | M1 · 3. Entornos virtuales: venv frente a conda | `polizas-api` | `git ls-files app.db` | `app.db` | Añadir `*.db` a `.gitignore` y eliminar del indice |
| H4 | No existe `.env.example` | No hay plantilla de variables de entorno | M8 · 3. De lo duro a lo flexible: variables de entorno | `polizas-api` | `ls .env.example` | `ls: cannot access '.env.example': No such file or directory` | Crear .env.example con valores de ejemplo |
| H5 | Secretos hardcodeados en `config.py` | Las claves estan en el código fuente | M8 · 3. De lo duro a lo flexible: variables de entorno | `config.py` | `cat config.py` | `# TODO: sacar esto a variables de entorno antes de subir a producción ` <br><br> ` SECRETO_FIRMA = "aseguradora-santo-tomas-2026-firma-7c1e" ` <br><br> ` CLAVE_API_REASEGURO = "rk-polizas-2026-4b9f0a3d" ` <br><br> ` DATABASE_URL = "sqlite:///app.db" ` <br><br> ` RUTA_MODELO = "modelo.pkl" ` <br><br> ` UMBRAL_ALTO_RIESGO = 0.6` | Mover a `.env` y leer con `BaseSettings` |
| H6 | | | | | | | |
| H7 | | | | | | | |
| H8 | | | | | | | |

**Reglas que se verifican automáticamente:**

- `Módulo · Sección` debe citar una lección que exista en los módulos 6 a 11, con el
  título tal como aparece en el menú lateral del material.
- **`SHA donde se observa`** es el commit donde el defecto todavía está: normalmente
  `v0-semilla`, la etiqueta del repositorio tal como se les entregó. El calificador hace
  *checkout* de ese commit para reproducir la evidencia. Si lo dejan en el commit final
  —donde ya está corregido— el comando no reproducirá nada y la fila no cuenta.
- `Comando de evidencia` se ejecuta ahí, con el servicio levantado. Escríbanlo contra
  `localhost:8000`; el calificador sustituye el puerto por el que use. Un comando `docker`
  también vale: se reproduce si hay Docker en la máquina que califica.
- `Salida obtenida` es literal, copiada de su terminal. **Se compara con lo que salga de
  verdad**, así que una salida inventada se detecta.
- Entre 8 y 14 hallazgos. Una fila que no corresponda a un defecto real resta la mitad de
  lo que suma una correcta: el máximo se alcanza con precisión, no con volumen.

---

# Parte C — Interpretación de las consultas

> Un párrafo por endpoint. Expliquen **los conteos que ustedes obtuvieron** con
> `contar_consultas.py`: por qué ese número, por qué cambia o no entre 10 y 2000
> pólizas, y qué estrategia dejaron en el código. Si un resultado los sorprendió,
> díganlo: eso se premia.

## `/polizas`

## `/polizas/{id}`

## `/siniestros`

## `/resumen`
