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
| 5 | B | Valentina | "No quiero añadir esas variables de compatibilidad... me parece innecesario." (Rechazo inicial) |
| 6 | A |  | "" |
| 7 | A |  | "" |
| 8 | A |  | "" |
| 9 | A |  | "" |


## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | 1. Congelado directo (rápido, pero incluye todo): <br><br>  `source .venv/bin/activate   # o .venv\Scripts\Activate.ps1 en Windows` <br><br> ` python -m pip freeze > requirements.txt` | es la opcion mas limpia y automatica | decidimos hacerlo al final para tener un requirements completo sin tener q actualizarlo cada tanto |
| 2 | # Python <br><br> `__pycache__/` <br><br> `*.py[cod]` <br><br> `*.pyc` <br><br> # Entorno virtual  <br><br> `.venv/` <br><br> `venv/` <br><br> `env/` <br><br> # Variables de entorno (secretos) <br><br> `.env` <br><br> `.env.*` <br><br> `!.env.example` <br><br> # Bases de datos SQLite  <br><br> `*.db` <br><br> `*.sqlite` <br><br> `*.sqlite3` <br><br> # Cachés de tests <br><br> `.pytest_cache/` <br><br> `.coverage` <br><br> `htmlcov/` <br><br> # Archivos de IDE <br><br> `.idea/` <br><br> `.vscode/` <br><br> `*.swp` | ya no tiene incluido el `.dockerignore` | corregimos el problema de excluor el `.dockerignore` |
| 4 | Crear `.env.example` con valores funcionales y `.env` con valores "reales". | El calificador copia `.env.example` a `.env` si no existe; los valores deben permitir que el servicio arranque. | Se copiaron los valores exactos que estaban hardcodeados en `config.py` a `.env`, y a `.env.example`. |
| 5 | Mover secretos a `.env` y leerlos con `BaseSettings` en `config.py`. | Cumple la restricción `B2` del taller ("La configuración se lee con `BaseSettings` desde `.env`"). | Se implementó con `pydantic-settings` y  `lru_cache.` |
| 5 | Añadir variables de módulo temporales en `config.py` para que el servicio arranque mientras se diagnostica. | Sin ellas, el servicio no arranca y eso impide seguir diagnosticando. Son temporales y se eliminarán en la `Parte B`. | Se añadieron al final de `config.py` con un comentario que indica que se eliminarán en la `Parte B`. |
| 1 |  |  |  |
| 1 |  |  |  |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | 2. Congelado selectivo (más limpio): Editar manualmente requirements.txt para poner solo las dependencias directas con ==, por ejemplo: <br><br> `fastapi==0.142.2` <br><br> `uvicorn==0.54.0` <br><br> `sqlalchemy==2.1.1` <br><br> `pydantic==2.13.5` <br><br> `scikit-learn==1.9.1` <br><br> `numpy==2.4.6` <br><br> `pytest==9.1.1` <br><br> `httpx==0.28.1` | al ser mas manuel es mas tediosa de implementar | optamos por la opcion 1 que propuso la ia que se encuentra en los aceptados |
| 2 | # Python <br><br> `__pycache__/` <br><br> `*.py[cod]` <br><br> `*.pyc` <br><br> # Entorno virtual  <br><br> `.venv/` <br><br> `venv/` <br><br> `env/` <br><br> # Variables de entorno (secretos) <br><br> `.env` <br><br> `.env.*` <br><br> `!.env.example` <br><br> # Bases de datos SQLite  <br><br> `*.db` <br><br> `*.sqlite` <br><br> `*.sqlite3` <br><br> # Cachés de tests <br><br> `.pytest_cache/` <br><br> `.coverage` <br><br> `htmlcov/` <br><br> # Archivos de IDE <br><br> `.idea/` <br><br> `.vscode/` <br><br> `*.swp` <br><br> # Docker <br><br> `.dockerignore` | incluia `.dockerignore` el cual es necesario para la parte del docker | quitamos el `.dockerignore` del `.gitignore` |
| 3 | Fusionar `H2` (`.gitignore` incompleto) y `H3` (`app.db` versionado) en un solo hallazgo. | Son defectos distintos: `H2` es el contenido de `.gitignore`; `H3` es que `app.db` está en el índice de Git. La solución de `H2` (editar `.gitignore`) no resuelve `H3` por sí sola; `H3` requiere `git rm --cached app.db`. Además, el taller pide entre 8 y 14 hallazgos, y fusionarlos reduce el conteo. | Se mantuvieron separados como `H2` y `H3`. `H3` tiene su propia evidencia (`git ls-files app.db`) y su propia corrección (`git rm --cached app.db`). |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
| 1 |  |  |  |
