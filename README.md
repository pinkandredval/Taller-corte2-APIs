# Pólizas API v0 — Servicio de gestión de pólizas y siniestros

Servicio de gestión de pólizas de la Aseguradora Santo Tomás. Registra pólizas y los siniestros que se les declaran, resume la cartera y puntúa el riesgo de cada póliza con un modelo, guardando cada predicción.

## Requisitos previos

- **Python 3.11.x** (verificar con `python --version`)
- **Git**
- **Docker** (opcional, para ejecución en contenedor)
- **SQLite** (incluido con Python)

> **Nota para Windows:** Si usas Windows nativo, asegúrate de tener Python 3.11.x instalado y los comandos funcionarán igual. Si usas WSL2, sigue las instrucciones para Linux.

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/polizas` | Crea una nueva póliza. |
| `GET` | `/polizas` | Lista las pólizas (paginación). |
| `GET` | `/polizas/{id}` | Consulta una póliza por su ID. |
| `GET` | `/resumen` | Devuelve un resumen de las pólizas. |
| `POST` | `/score` | Calcula el riesgo de una póliza. |

## 1. Clonar el repositorio

```bash
git clone https://github.com/pinkandredval/Taller-corte2-APIs
cd polizas-api
```

## 2. Crear y activar el entorno virtual

**Linux / macOS / WSL:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> **Importante:** A partir de aquí, todos los comandos de Python se ejecutan con `python -m` para garantizar compatibilidad entre sistemas operativos.

## 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Configurar variables de entorno

Copia el archivo de ejemplo y ajústalo si es necesario:

```bash
cp .env.example .env
```

El archivo `.env` contiene:

```env
# .env — NO subir a Git
SECRETO_FIRMA=tu-secreto-de-firma
CLAVE_API_REASEGURO=tu-clave-de-reaseguro
DATABASE_URL=sqlite:///./app.db
RUTA_MODELO=modelo.pkl
UMBRAL_ALTO_RIESGO=0.6
```

- **`DATABASE_URL`**: por defecto usa SQLite local. Para producción, cámbiala a PostgreSQL.
- **`SECRETO_FIRMA`**: secreto para firmar las pólizas. Puedes generar uno seguro con: `python -c "import secrets; print(secrets.token_hex(32))"`.
- **`UMBRAL_ALTO_RIESGO`**: umbral para clasificar una póliza como de alto riesgo.
- **`RUTA_MODELO`**: el archivo `modelo.pkl` ya está incluido en el repositorio. Si se borra, el endpoint `/score` fallará.

> **Nunca subas el archivo `.env` al repositorio.** Está incluido en `.gitignore`.

## 5. Aplicar migraciones de base de datos

Asegúrate de tener una base de datos vacía (o bórrala si ya existe) y ejecuta:

```bash
python -m alembic upgrade head
```

Esto creará las tablas `polizas`, `siniestros` y `predicciones` en la base definida por `DATABASE_URL`.

## 6. Ejecutar el servicio en local

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

El servicio estará disponible en:

- API: [http://localhost:8000](http://localhost:8000)
- Documentación interactiva (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Documentación alternativa (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

> **Nota:** Para desarrollo y pruebas locales, puedes añadir `--reload` al comando anterior si deseas que el servidor se reinicie automáticamente al guardar cambios. Sin embargo, no se debe usar en producción.

- Recuerda que para ejecutar comandos de prueba (como `curl`), debes abrir **otra terminal**, activar el entorno virtual (`source .venv/bin/activate` o `.venv\Scripts\Activate.ps1`) y ejecutar los comandos contra `http://localhost:8000`.

## 7. Ejecutar pruebas

Asegúrate de tener el entorno virtual activado y las dependencias instaladas. Luego:

```bash
python -m pytest
```

Para ver el detalle de cada prueba:
```bash
python -m pytest -v
```

La batería de pruebas incluye:

- `tests/test_contrato.py`: contrato de la API (no modificar).
- `tests/test_api.py`: pruebas originales del servicio.
- `tests/test_ia_corregido.py`: pruebas corregidas de la auditoría de IA (Parte D).

*Nota:* El archivo `ia_tests_propuesta.py` en la raíz contiene los tests defectuosos de la IA y **no se ejecuta por defecto** con `pytest`. Para correrlo explícitamente: `python -m pytest ia_tests_propuesta.py -v`.

## 8. Ejecutar con Docker

- Antes de iniciar el docker pausar el uvicorn ya q usan el mismo puerto.
- Para construir y ejecutar la imagen, **NO** actives el entorno virtual (`source .venv/bin/activate`). Abre una terminal nueva, sin el `.venv` activo, y ejecuta los comandos de Docker.

### Construir la imagen

```bash
docker build -t polizas-api:latest .
```

### Ejecutar el contenedor

Tienes dos opciones dependiendo de tu entorno:

**Opción A (Recomendada para pruebas rápidas usando la plantilla):**
```bash
docker run -d -p 8000:8000 --name polizas-api --env-file .env.example polizas-api:latest
```

**Opción B (Usando tus propias variables de entorno reales):**
```bash
docker run -d -p 8000:8000 --name polizas-api --env-file .env polizas-api:latest
```

> **Nota:** La `Opción A` usa `.env.example` para que el contenedor arranque inmediatamente sin requerir configuración previa. La `Opción B` usa tu archivo `.env` local, que es lo ideal si has cambiado los secretos o la configuración. Sin estas variables, la aplicación no arranca porque `Settings` requiere `SECRETO_FIRMA` y `CLAVE_API_REASEGURO`.

El servicio estará disponible en [http://localhost:8000](http://localhost:8000). El contenedor ejecuta automáticamente `alembic upgrade head` antes de arrancar `uvicorn` (ver `Dockerfile`).

### Detener y eliminar el contenedor 
(solo si no haras la pruena del contenedor, sino hacerlo al final de la prueba)

```bash
docker stop polizas-api
docker rm polizas-api
```

## 9. Probar el contenedor (para la sustentación)

Una vez que el contenedor esté corriendo (ver sección 8), puedes verificar su funcionamiento con los siguientes comandos. Abre una terminal nueva (sin el entorno virtual activado) y ejecútalos:

### 1. Verificar que el contenedor está saludable
```bash
docker ps
```
Deberías ver el contenedor con estado `Up` y un health check en `healthy`.

### 2. Probar el endpoint de salud
```bash
curl -i http://localhost:8000/health
```
Debe devolver `200 OK` con `{"status":"ok","database":"ok"}`.

### 3. Crear una póliza de prueba
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/polizas \
  -H "Content-Type: application/json" \
  -d '{"numero":"POL-DOCKER-001","asegurado":"Ana Docker","tipo":"auto","prima":500.0,"fecha_inicio":"2026-01-01","fecha_fin":"2027-01-01"}'
```
Debe devolver `201`.

### 4. Verificar que la póliza se creó
```bash
curl -s http://localhost:8000/polizas
```
Debe devolver un JSON con la póliza `POL-DOCKER-001`.

### 5. Demostración de persistencia (Caso A: reinicio)
```bash
docker restart polizas-api
sleep 5
curl -s http://localhost:8000/polizas
```
Los datos **se conservan** porque el sistema de archivos del contenedor no se destruye.

### 6. Demostración de persistencia (Caso B: borrar y recrear)
```bash
docker rm -f polizas-api
docker run -d -p 8000:8000 --name polizas-api --env-file .env.example polizas-api:latest
sleep 5
curl -s http://localhost:8000/polizas
```
Los datos **se pierden** (el nuevo contenedor parte de la imagen original, sin `app.db`).

> **Explicación para la sustentación:** La persistencia de datos entre contenedores requiere un volumen (`-v`), que está fuera del alcance de este taller. Lo que se demuestra aquí es que el contenedor es efímero: al borrarlo, su sistema de archivos se destruye.

## 10. Entregables del taller

Los siguientes archivos contienen los resultados del taller y están en la raíz del proyecto:

- `HALLAZGOS.md`: Resultados de la Parte A (auditoría de contratos y pruebas).
- `CONSULTAS.csv`: Resultados de la Parte C (medición de consultas SQL).
- `DICTAMEN_IA.md`: Resultados de la Parte D (auditoría de los tests de IA).
- `BITACORA_IA.md`: Bitácora de uso de IA (Parte E).
- `EQUIPO.md`: Integrantes e identidades git.
- `tests/test_ia_corregido.py`: Tests corregidos de la Parte D.

## 11. Estructura del proyecto

```
polizas-api/
├── alembic/                  # Configuración y migraciones de Alembic
│   ├── versions/             # Revisiones generadas (una por cambio de esquema)
│   ├── env.py                # Configuración del entorno de Alembic
│   └── script.py.mako        # Plantilla para generar nuevas revisiones
├── plantillas/               # Plantillas de los entregables del taller
│   ├── BITACORA_IA.md        # Plantilla de bitácora
│   ├── CONSULTAS.csv         # Plantilla para la Parte C
│   ├── DICTAMEN_IA.md        # Plantilla para la Parte D
│   ├── EQUIPO.md             # Plantilla para declarar el equipo
│   └── HALLAZGOS.md          # Plantilla para la Parte A
├── tests/                    # Pruebas automatizadas
│   ├── test_api.py           # Pruebas originales del servicio
│   ├── test_contrato.py      # Batería de 12 tests del contrato (no modificar)
│   └── test_ia_corregido.py  # Pruebas corregidas de la auditoría de IA (Parte D)
├── .dockerignore             # Archivos excluidos del contexto de Docker
├── .env                      # Variables de entorno reales (NO se sube a Git)
├── .env.example              # Plantilla de variables de entorno (SÍ se sube a Git)
├── .gitignore                # Archivos excluidos del control de versiones
├── alembic.ini               # Configuración principal de Alembic
├── app.db                    # Base de datos SQLite (generada localmente, NO se sube a Git)
├── config.py                 # Configuración con Pydantic Settings
├── contar_consultas.py       # Script para medir consultas SQL (Parte C)
├── database.py               # Conexión a base de datos y get_db
├── Dockerfile                # Imagen Docker multietapa
├── ENUNCIADO.md              # Instrucciones originales del taller
├── esquemas.py               # Esquemas Pydantic (entrada y salida)
├── ia_tests_propuesta.py     # Tests defectuosos generados por IA (Parte D)
├── main.py                   # Punto de entrada de FastAPI y endpoints
├── modelo.pkl                # Modelo de machine learning serializado
├── modelos.py                # Modelos de SQLAlchemy
├── README.md                 # Este archivo
├── requirements.in           # Dependencias directas sin fijar
├── requirements.txt          # Dependencias fijadas (generadas desde requirements.in)
├── sembrar_datos.py          # Script para poblar la base de datos
└── verificar_entrega.py      # Script del profesor para comprobar entregables
```

## 12. Notas adicionales

- Recuerda que para ejecutar comandos de prueba (como `curl`), debes abrir **otra terminal**, activar el entorno virtual.
  ```bash
  source .venv/bin/activate
  ```
   ```bash
  .venv\Scripts\Activate.ps1
  ```

- Recuerda volver a activar 
  ```bash
  python -m uvicorn main:app --host 0.0.0.0 --port 8000
  ```

- **Migraciones**: Si haces cambios en los modelos, genera una nueva revisión con:
  ```bash
  python -m alembic revision --autogenerate -m "descripción del cambio"
  ```
  ```bash
  python -m alembic upgrade head
  ```
- **Datos de prueba**: Para poblar la base con datos sintéticos, ejecuta:
  ```bash
  python -m sembrar_datos --polizas 10
  ```
- **Medición de consultas (Parte C)**: Para reproducir los conteos de la Parte C:
  ```bash
  python -m contar_consultas
  ```
  Esto generará el archivo `CONSULTAS.csv` con los resultados.
- **Docker en Windows/Mac**: Asegúrate de que Docker Desktop esté en ejecución antes de usar `docker build` y `docker run`.

## 13. Solución de problemas

- **Error `ModuleNotFoundError`**: Asegúrate de tener el entorno virtual activado y las dependencias instaladas.
- **Error de base de datos bloqueada**: Cierra cualquier proceso que esté usando `app.db` y vuelve a intentar.
- **Error en `alembic upgrade head`**: Verifica que `DATABASE_URL` esté bien definida en `.env` y que la base de datos no tenga tablas previas.

---

**Equipo:** Kevin Leonardo Chaparro Reyes, Valentina Muñoz Palma, Paula Margarita Triana Ancinez  
**Curso:** Python para Desarrollo de APIs e IA — USTA — 2026-II
