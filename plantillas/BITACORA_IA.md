# Bitácora de uso de IA

**Grupo:**  1  · **Integrantes:**  Kevin Leonardo Chaparro Reyes, Valentina Muñoz Palma, Paula Margarita Triana Ancinez

**Herramientas usadas:** deep seek

> Las tres secciones son obligatorias. **`## Rechazado` es la que se califica.**
> Una bitácora que solo lista prompts aceptados vale la mitad.

## Prompts

| # | Parte | Quién | Prompt (resumido si es largo) |
|---|-------|-------|-------------------------------|
| 1 | A | Valentina | "H1=prefiero la opción 1 de freezer, pero ¿la hago ya o luego?"|
| 2 | A | Valentina | "H2=¿por qué incluyes el .dockerignore en el .gitignore?" |
| 3 | A | Valentina | "H2=sigo sin entender lo de no unir H2 con H3" |
| 4 | B | Valentina | "Quiero solucionar el H4." (Se adjuntó config.py con secretos hardcodeados). |
| 5 | A | Valentina | "No quiero añadir esas variables de compatibilidad... me parece innecesario." (Rechazo inicial) |
| 6 | A | Margarita | "Sale este error: `NOT NULL constraint failed: polizas.prima` al hacer PUT con solo `{"prima": 600}`" (H13). |
| 7 | A | Margarita | "Ya corregí el hallazgo 15 pero sigue apareciendo `None` en `asegurado`." (H15). |
| 8 | A | Valentina | "Ya revisé `tipo` y `estado`. Sale esto pero aún no he hecho la corrección. ¿Cómo valido `tipo`, `estado`, `prima`? ¿Dónde va el `@model_validator`?" (H17, H18, H19). |
| 9 | A | Margarita | "Sale esto pero aún no he hecho la corrección" (H18, se adjuntó salida con `tipo: "invalido"`). |
| 10 | A | Margarita | "¿Es mejor unir el H14 con el H18? Nos dimos cuenta que es mejor unir el H13 y el H18, o se unen los 3?" (Unificación de hallazgos). |
| 11 | A | Margarita| "El servicio no arranca, sale `no such table: polizas`" (Alembic). |
| 12 | A | Margarita | "Los comandos `curl.exe` no dan el JSON, sale `JSON decode error`" (PowerShell). |
| 13 | A |  | "" |
| 14 | A |  | "" |
| 15 | A |  | "" |
| 16 | A |  | "" |


## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | 1. Congelado directo (rápido, pero incluye todo): <br><br>  `source .venv/bin/activate   # o .venv\Scripts\Activate.ps1 en Windows` <br><br> ` python -m pip freeze > requirements.txt` | es la opcion mas limpia y automatica | decidimos hacerlo al final para tener un requirements completo sin tener q actualizarlo cada tanto |
| 2 | # Python <br><br> `__pycache__/` <br><br> `*.py[cod]` <br><br> `*.pyc` <br><br> # Entorno virtual  <br><br> `.venv/` <br><br> `venv/` <br><br> `env/` <br><br> # Variables de entorno (secretos) <br><br> `.env` <br><br> `.env.*` <br><br> `!.env.example` <br><br> # Bases de datos SQLite  <br><br> `*.db` <br><br> `*.sqlite` <br><br> `*.sqlite3` <br><br> # Cachés de tests <br><br> `.pytest_cache/` <br><br> `.coverage` <br><br> `htmlcov/` <br><br> # Archivos de IDE <br><br> `.idea/` <br><br> `.vscode/` <br><br> `*.swp` | ya no tiene incluido el `.dockerignore` | corregimos el problema de excluor el `.dockerignore` |
| 4 | Crear `.env.example` con valores funcionales y `.env` con valores "reales". | El calificador copia `.env.example` a `.env` si no existe; los valores deben permitir que el servicio arranque. | Se copiaron los valores exactos que estaban hardcodeados en `config.py` a `.env`, y a `.env.example`. |
| 5 | Mover secretos a `.env` y leerlos con `BaseSettings` en `config.py`. | Cumple la restricción `B2` del taller ("La configuración se lee con `BaseSettings` desde `.env`"). | Se implementó con `pydantic-settings` y  `lru_cache.` |
| 5 | Añadir variables de módulo temporales en `config.py` para que el servicio arranque mientras se diagnostica. | Sin ellas, el servicio no arranca y eso impide seguir diagnosticando. Son temporales y se eliminarán en la `Parte B`. | Se añadieron al final de `config.py` con un comentario que indica que se eliminarán en la `Parte B`. |
| 6 | Usar `datos.model_dump(exclude_unset=True)` para que el PUT sea parcial (H13). | Es la solución canónica de FastAPI + Pydantic para PUT parciales. Cumple B6. | Se aplicó en `main.py`. Verificamos con una póliza nueva que los campos no enviados conservan sus valores. |
| 7 | Añadir `return` al validador `normalizar_asegurado` (H15). | El validador no devolvía el valor, dejando `asegurado = None`. Es el defecto exacto del M7 · 6. | Verificamos que las pólizas nuevas ya tienen `asegurado` con valor. Las viejas siguen con `None` porque se crearon antes. |
| 8 | Cambiar `siniestros: list[dict]` por `list[SiniestroEntrada]` y ajustar `main.py` (H16). | Sin el tipado, Pydantic no valida los campos internos y el endpoint falla al convertir `"invalida"` a fecha. Cumple B7. | Verificamos que ahora devuelve 422 en lugar de 500. |
| 9 | Añadir `@model_validator(mode="after")` que valide `fecha_fin > fecha_inicio` (H17). | Cumple B7. Sin él, se aceptan pólizas con fechas invertidas. | Verificamos que ahora devuelve 422 con el mensaje `"fecha_fin debe ser posterior a fecha_inicio"`. |
| 9 | Cambiar `tipo: str` por `Literal["auto", "hogar", "vida"]` en `PolizaEntrada` y `PolizaActualizacion` (H18). | El campo aceptaba cualquier string. Es el defecto del M7 · 4. | Verificamos que ahora devuelve 422. |
| 9 | Cambiar `estado: str` por `Literal["abierto", "pagado", "rechazado"]` en `SiniestroEntrada` (H19). | El campo aceptaba cualquier string. Es el mismo tipo de defecto que H18. | Verificamos que ahora devuelve 422. |
| 10 | Unificar H18 (`tipo` en POST) y H19 (`tipo` en PUT) en una sola fila de `HALLAZGOS.md`. | Son el mismo defecto (`Literal` faltante) en dos esquemas distintos. Reduce filas y gana precisión. | Se mantuvo H19 (`estado`) separado porque afecta a un campo distinto. |
| 11 | Escribir la revisión de Alembic a mano (`op.create_table(...)`) porque la generada estaba vacía (Problema técnico: Alembic). | Sin las tablas, el servicio devolvía `no such table: polizas`. Necesitábamos el servicio funcionando para diagnosticar. | Escribimos la revisión manualmente y aplicamos `python -m alembic upgrade head` sobre la base temporal. |
| 12 | Usar `Invoke-RestMethod` en lugar de `curl.exe` para enviar JSON. Usar `-o $null` y `Select-Object -First 1` en lugar de `-o NUL` y `head -1` (Problema técnico: PowerShell). | Los comandos `curl.exe` daban `JSON decode error` y no podíamos probar los endpoints. | Adaptamos todos los comandos de prueba a PowerShell. |
| 1 |  |  |  |
| 1 |  |  |  |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | Congelado selectivo (más limpio): Editar manualmente requirements.txt para poner solo las dependencias directas con ==, por ejemplo: <br><br> `fastapi==0.142.2` <br><br> `uvicorn==0.54.0` <br><br> `sqlalchemy==2.1.1` <br><br> `pydantic==2.13.5` <br><br> `scikit-learn==1.9.1` <br><br> `numpy==2.4.6` <br><br> `pytest==9.1.1` <br><br> `httpx==0.28.1` | al ser mas manual es mas tediosa de implementar | optamos por la opcion 1 que propuso la ia que se encuentra en los aceptados |
| 2 | # Python <br><br> `__pycache__/` <br><br> `*.py[cod]` <br><br> `*.pyc` <br><br> # Entorno virtual  <br><br> `.venv/` <br><br> `venv/` <br><br> `env/` <br><br> # Variables de entorno (secretos) <br><br> `.env` <br><br> `.env.*` <br><br> `!.env.example` <br><br> # Bases de datos SQLite  <br><br> `*.db` <br><br> `*.sqlite` <br><br> `*.sqlite3` <br><br> # Cachés de tests <br><br> `.pytest_cache/` <br><br> `.coverage` <br><br> `htmlcov/` <br><br> # Archivos de IDE <br><br> `.idea/` <br><br> `.vscode/` <br><br> `*.swp` <br><br> # Docker <br><br> `.dockerignore` | incluia `.dockerignore` el cual es necesario para la parte del docker | quitamos el `.dockerignore` del `.gitignore` |
| 3 | Fusionar `H2` (`.gitignore` incompleto) y `H3` (`app.db` versionado) en un solo hallazgo. | Son defectos distintos: `H2` es el contenido de `.gitignore`; `H3` es que `app.db` está en el índice de Git. La solución de `H2` (editar `.gitignore`) no resuelve `H3` por sí sola; `H3` requiere `git rm --cached app.db`. Además, el taller pide entre 8 y 14 hallazgos, y fusionarlos reduce el conteo. | Se mantuvieron separados como `H2` y `H3`. `H3` tiene su propia evidencia (`git ls-files app.db`) y su propia corrección (`git rm --cached app.db`). |
| 9 | Documentar `PolizaActualizacion.prima` como hallazgo. | Al revisar el código, `prima` **ya tiene** `gt=0`. No es un defecto. Documentarlo restaría puntos porque el taller dice: *"Una fila que no corresponda a un defecto real resta la mitad"*. | No se documentó. Se verificó que la validación funciona (devuelve 422 con `prima = -100`). |
| 10 | Unificar H14 (`response_model`) con H18 (`tipo` sin validar). | Son defectos de módulos distintos: H14 es M6 · 5 y H18 es M7 · 4. Fusionarlos mezclaría citas de módulos diferentes y rompería el parser de `HALLAZGOS.md`. | Se mantuvieron separados. H18 se unió con H19 por ser del mismo módulo (M7 · 4). |
| 10 | Unificar H13 (PUT no parcial) con H18 (`tipo` sin validar).| Son defectos distintos: H13 es M6 · 5 y H18 es M7 · 4. Además, tienen causas y soluciones distintas (`model_dump()` sin `exclude_unset` vs. `Literal` faltante). Fusionarlos confundiría al calificador. | Se mantuvieron separados. H13 es fila independiente; H18 se unifica solo con H19. |
| 12 | Usar `curl.exe` con `-o NUL` y `head -1` para los comandos de evidencia. | En PowerShell, `-o NUL` no funciona correctamente (devuelve `422000` en lugar de `422`), y `head -1` no existe (es un comando de Linux). | Usamos `-o $null` en lugar de `-o NUL`, y `Select-Object -First 1` en lugar de `head -1`. |
| 12 | Usar `curl.exe` para enviar JSON en PowerShell. | PowerShell rompe las comillas anidadas del JSON, dando `JSON decode error`. No podíamos probar los endpoints. | Usamos `Invoke-RestMethod` con `ConvertTo-Json`, que maneja el JSON correctamente. |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
