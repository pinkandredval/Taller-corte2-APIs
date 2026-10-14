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
| H6 | Sesión de `BD` global reutilizada en todas las peticiones | `sesion = SessionLocal()` en `database.py` | M8 · 4. Inyección de dependencias con Depends | `database.py` | `grep -n "sesion = SessionLocal" database.py` | `16:sesion = SessionLocal()` | Eliminar sesión global; crear `get_db` con `yield` |
| H7 | No existe función `get_db` | `database.py` no define generador con `yield` | M8 · 4. Inyección de dependencias con Depends | `main.py` | `grep -c "def get_db" database.py` | `0` | Crear `get_db` como generador con `yield` |
| H8 | Las tablas se crean al arrancar el servicio | `Base.metadata.create_all(engine)` en `main.py` | M9 · 6. Modelado de BD y migraciones con Alembic | `main.py` y `env.py` | `grep -n "create_all" main.py` | `18:Base.metadata.create_all(engine)` | Eliminar; usar Alembic |
| H9 | `GET /health` devuelve `404` | No existe la ruta | M6 · 5. Routing y CRUD | | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/health` | `404` | Crear endpoint `/health` |
| H10 | `GET /polizas/99999` devuelve `500` en lugar de `404` | El handler devuelve dict en lugar de lanzar `HTTPException(404)`; la sesión global está corrupta | M6 · 5. Routing y CRUD | | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/polizas/99999` | `500` | Lanzar `HTTPException(404)` y usar `get_db` |
| H11 | `POST /polizas` no devuelve `201`	 | No se declara `status_code=201` | M6 · 5. Routing y CRUD | | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/polizas \  -H "Content-Type: application/json" \  -d '{"numero":"POL-TEST-001","asegurado":"Juan Perez","tipo":"auto","prima":500.0,"fecha_inicio":"2024-01-01","fecha_fin":"2024-12-31"}'` | `500` | `model_dump(exclude_unset=True)` |
| H12 | `POST /polizas` duplicado devuelve `500` | No se captura `IntegrityError` | M6 · 5. Routing y CRUD | | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/polizas \  -H "Content-Type: application/json" \  -d '{"numero":"POL-TEST-001","asegurado":"Otro","tipo":"vida","prima":300.0,"fecha_inicio":"2024-02-01","fecha_fin":"2025-02-01"}'` | `500` | `try/except IntegrityError → HTTPException(409)` |
| H13 | `PUT /polizas/1` con solo `{"prima":600}` devuelve `500` | No se usa `exclude_unset` | M6 · 5. Routing y CRUD | | `$body = @{ `<br>` prima = 600.0 `<br>` } \| ConvertTo-Json `<br>` Invoke-RestMethod -Uri http://localhost:8000/polizas/1 -Method PUT -ContentType "application/json" -Body $body` | `200` con `asegurado: "", tipo: "", fecha_fin: ""` | Agregar: `model_dump(exclude_unset=True)` |
| H14 | Ninguna ruta declara `response_model` | No se definen esquemas de salida | M6 · 5. Routing y CRUD | | `grep -c "response_model" main.py` | `0` | Definir esquemas y declarar `response_model` |
| H15 | `GET /polizas` devuelve `"asegurado":null` en todas las pólizas | El validador `normalizar_asegurado` no tiene return; devuelve `None` en lugar del valor normalizado | M7 · 6. Validadores de campo | | `curl.exe -s localhost:8000/polizas \| python -c "import sys,json; d=json.load(sys.stdin); print(d[0].get('asegurado'))"`| `None` | Añadir return al validador|
| H16 | `POST /polizas` acepta siniestros con datos inválidos (monto negativo, fecha inválida, descripción vacía) | El campo siniestros está tipado como `list[dict]` en lugar de `list[SiniestroEntrada]`; Pydantic no valida los campos internos | M7 · 5. Modelos anidados y topología jerárquica | | `curl.exe -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{\"numero\":\"POL-2026-99999\",\"asegurado\":\"Test\",\"tipo\":\"auto\",\"prima\":100,\"fecha_inicio\":\"2026-01-15\",\"fecha_fin\":\"2027-01-15\",\"siniestros\":[{\"monto\":-500,\"descripcion\":\"\",\"fecha\":\"invalida\"}]}'` | `HTTP/1.1 500 Internal Server Error `<br>` date: Tue, 13 Oct 2026 05:39:46 GMT `<br>` server: uvicorn `<br>` content-length: 21 `<br>` content-type: text/plain; charset=utf-8 `<br>` Internal Server Error` | Cambiar a `list[SiniestroEntrada]` |
| H17 | `POST /polizas` acepta pólizas con fecha_fin anterior a fecha_inicio | No existe un `model_validator` que verifique la coherencia de fechas | M7 · 6. Validadores de campo | | `$body = @{ `<br>` numero = "POL-2026-99998" `<br>` asegurado = "Test" `<br>` tipo = "auto" `<br>` prima = 100 `<br>` fecha_inicio = "2027-01-14" `<br>` fecha_fin = "2026-01-15" `<br>` } \| ConvertTo-Json `<br>` Invoke-RestMethod -Uri http://localhost:8000/polizas -Method POST -ContentType "application/json" -Body $body` | Creo la poliza con fechas invertidas: ` `<br>` id : 14 `<br>` numero : POL-2026-99999 `<br>` asegurado : Test `<br>` tipo : auto `<br>` fecha_inicio : 2027-01-14 `<br>` token_firma : 9b736ac4910fd9716a7b5399491710257ab23dc13618661d291c04ba716ac4f6 `<br>` prima : 100,0 `<br>` fecha_fin : 2026-01-15` | Añadir `@model_validator(mode='after')` que valide fecha_fin > fecha_inicio |
| H18 | `POST /polizas` y `PUT /polizas/{id}` aceptan cualquier valor en tipo (ej: "invalido") | Los campos tipo en `PolizaEntrada (str)` y `PolizaActualizacion (Optional[str])` no tienen restricción; la descripción `"auto, hogar o vida"` no es validación | M7 · 4. El poder de Field | | Evidencia `POST`: `  `<br>` $body = @{ `<br>` numero = "POL-2026-88888" `<br>` asegurado = "Test" `<br>` tipo = "invalido" `<br>` prima = 100 `<br>` fecha_inicio = "2026-01-15" `<br>` fecha_fin = "2027-01-15" `<br>` } \| ConvertTo-Json `<br>` Invoke-RestMethod -Uri http://localhost:8000/polizas -Method POST -ContentType "application/json" -Body $body `<br>` ` Evidencia `PUT`: ` `<br>` $body = @{ `<br>` tipo = "invalido" `<br>` } \| ConvertTo-Json `<br>` Invoke-RestMethod -Uri http://localhost:8000/polizas/16 -Method PUT -ContentType "application/json" -Body $body `  | la póliza se creó con tipo: `"invalido"`, en ambos esquemas. Eso significa que no hay validación de `tipo` | Cambiar a `Literal["auto", "hogar", "vida"]` en ambos esquemas |
| H19 | `POST /polizas/{id}/siniestros` acepta cualquier valor en estado (ej: "invalido") | El campo estado es `str` sin restricción | M7 · 4. El poder de Field | | `$body = @{ `<br>` fecha = "2026-01-15" `<br>` monto = 100 `<br>` descripcion = "Test" `<br>` estado = "invalido" `<br>` } \| ConvertTo-Json `<br>` Invoke-RestMethod -Uri http://localhost:8000/polizas/1/siniestros -Method POST -ContentType "application/json" -Body $body` | la póliza se creó con estado: `"invalido"` | Cambiar a `Literal["abierto", "pagado", "rechazado"]` |
| H20 | | | | | | | |
| H21 | | | | | | | |
| H22 | | | | | | | |
| H23 | | | | | | | |
| H24 | | | | | | | |

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
