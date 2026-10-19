# Dictamen sobre `ia_tests_propuesta.py` — Parte D

**Grupo:**  1  · **Integrantes:**  Kevin Leonardo Chaparro Reyes, Valentina Muñoz Palma, Paula Margarita Triana Ancinez

> Tres defectos. Las cuatro secciones de cada uno son obligatorias y se parsean.
> El peso está en **«Cómo lo comprobamos»**, y la comprobación tiene una forma
> concreta: **una mutación**. Introduzcan a propósito un defecto en el servicio,
> muestren que el test original sigue en verde y que el corregido se pone en rojo,
> y vuelvan a dejar el servicio como estaba. Afirmar que un test es malo no vale;
> demostrar que no detecta nada, sí.

## Defecto 1

- **Qué está mal:** La IA usó aserciones triviales en 5 de los 6 tests (ej. `assert r.status_code in (200, 201, 422)`, `assert r.status_code < 500`, `assert "puntaje" in r.json() or "error" in r.json()`). Esto hace que los tests pasen sin importar si el código cumple el contrato real.
- **Por qué es un defecto** (M10 · 4. Framework pytest): Un buen test debe fallar cuando el código no cumple lo que promete. Al aceptar múltiples códigos, el test se vuelve ciego a los errores de contrato. El taller exige que los tests propios detecten fallos, no que los ignoren. 
- **Cómo lo comprobamos:**

# mutación
```diff
# Mutación: en main.py
- @app.post("/polizas", status_code=201, response_model=PolizaSalida)
+ @app.post("/polizas", status_code=200, response_model=PolizaSalida) #mutación

- @app.get("/polizas/{id_poliza}", response_model=PolizaSalida)
+ @app.get("/polizas/{id_poliza}", status_code=200, response_model=PolizaSalida) #mutacion

# Para el 404, hacemos que devuelva un objeto falso en lugar de lanzar la excepción
  @app.get("/polizas/{id_poliza}", response_model=PolizaSalida)
  def obtener_poliza(id_poliza: int, db: Session = Depends(get_db)):
      poliza = db.get(Poliza, id_poliza)
      if poliza is None:
-         raise HTTPException(status_code=404, detail="...")
+         return Poliza(id=0, numero="POL-FAKE", asegurado="Fake", tipo="auto", prima=0, fecha_inicio="2026-01-01", fecha_fin="2026-12-31", token_firma="fake") #mutación
      return poliza
```
# test original, en verde
```
# Salida de pytest con el test ORIGINAL sobre el servicio mutado
codigo de evidencia: python -m pytest ia_tests_propuesta.py -v

ia_tests_propuesta.py::test_crear_poliza_responde PASSED                                                                                                      
ia_tests_propuesta.py::test_primas_variadas_son_aceptadas PASSED                                                                                              
ia_tests_propuesta.py::test_consultar_poliza_inexistente PASSED                                                                                               
ia_tests_propuesta.py::test_listar_polizas_no_falla PASSED                                                                                                    
ia_tests_propuesta.py::test_resumen_devuelve_lista PASSED                                                                                                     
ia_tests_propuesta.py::test_score_de_poliza_recien_creada PASSED 

6 passed, 1 warning in 5.88s
```
# test corregido, en rojo
```
# Salida de pytest con el test CORREGIDO sobre el servicio mutado
codigo de evidencia: python -m pytest tests/test_ia_corregido.py
FAILED tests/test_ia_corregido.py::test_crear_poliza_responde - AssertionError: Se esperaba 201, se obtuvo 200
FAILED tests/test_ia_corregido.py::test_primas_variadas_son_aceptadas - AssertionError: Se esperaba 201, se obtuvo 200
FAILED tests/test_ia_corregido.py::test_consultar_poliza_inexistente - AssertionError: Se esperaba 404, se obtuvo 200

3 failed, 3 passed, 1 warning in 5.49s
```

- **Corrección:**  Se reescribieron las aserciones en tests/test_ia_corregido.py para que exijan los códigos de estado exactos del contrato (201 para creación, 404 para no encontrado, 200 para consultas exitosas) y se eliminaron los operadores or que ocultaban errores.
```python
# Corrección en test_crear_poliza_responde
assert r.status_code == 201

# Corrección en test_primas_variadas_son_aceptadas
assert r.status_code == 201

# Corrección en test_consultar_poliza_inexistente
assert r.status_code == 404

# Corrección en test_listar_polizas_no_falla
assert r.status_code == 200

# Corrección en test_score_de_poliza_recien_creada
assert r.status_code == 200
assert "puntaje" in r.json()
```

## Defecto 2

- **Qué está mal:** El `get_db` que el test registra en `dependency_overrides` es una función local, distinta de `database.get_db`, por lo que el override no se aplica y las pruebas escriben en la base de datos real. Además, solo verifican el código de estado, no el contenido de la respuesta, así que un servicio que devuelva datos corruptos sigue pasando.
- **Por qué es un defecto** (M10 · 5. TestClient de FastAPI): El taller exige que los tests usen `app.dependency_overrides` con una base de datos temporal real (B8). Usar un `MagicMock` no prueba la persistencia ni la integridad de los datos.
- **Cómo lo comprobamos:**

# mutación
```diff
# Mutación: en main.py, alteramos el número de póliza antes de devolverlo
      db.commit()
      db.refresh(poliza)
+     poliza.numero = "POL-CORRUPTO"  # Mutación: devolvemos un dato incorrecto
      return poliza 
```
# test original, en verde
```
# Salida de pytest con el test ORIGINAL sobre el servicio mutado
codigo de evidencia: python -m pytest ia_tests_propuesta.py -v

ia_tests_propuesta.py::test_crear_poliza_responde PASSED                                                           
ia_tests_propuesta.py::test_primas_variadas_son_aceptadas PASSED                                                   
ia_tests_propuesta.py::test_consultar_poliza_inexistente PASSED                                                    
ia_tests_propuesta.py::test_listar_polizas_no_falla PASSED                                                         
ia_tests_propuesta.py::test_resumen_devuelve_lista PASSED                                                          
ia_tests_propuesta.py::test_score_de_poliza_recien_creada PASSED  

6 passed, 1 warning in 5.88s
```
# test corregido, en rojo
```python
# Salida de pytest con el test CORREGIDO sobre el servicio mutado
codigo de evidencia: python -m pytest tests/test_ia_corregido.py
def test_crear_poliza_responde():
        datos = _poliza()
        r = cliente.post("/polizas", json=datos)
        assert r.status_code == 201, f"Se esperaba 201, se obtuvo {r.status_code}"
>       assert r.json()["numero"] == datos["numero"]
E       AssertionError: assert 'POL-CORRUPTO' == 'POL-2026-ABC02'
E         
E         - POL-2026-ABC02
E         + POL-CORRUPTO

tests\test_ia_corregido.py:81: AssertionError
__________________________________________ test_primas_variadas_son_aceptadas ___________________________________________

    def test_primas_variadas_son_aceptadas():
        primas = [1.0, 99.99, 123_456.78, 1_500_000.5, 5_000_000.0]
        for i, prima in enumerate(primas):
            datos = _poliza(numero=f"POL-2026-VAR{i:02d}", prima=prima)
            r = cliente.post("/polizas", json=datos)
            assert r.status_code == 201, f"Se esperaba 201, se obtuvo {r.status_code}"
>           assert r.json()["numero"] == datos["numero"]
E           AssertionError: assert 'POL-CORRUPTO' == 'POL-2026-VAR00'
E             
E             - POL-2026-VAR00
E             + POL-CORRUPTO

tests\test_ia_corregido.py:91: AssertionError

FAILED tests/test_ia_corregido.py::test_crear_poliza_responde - AssertionError: assert 'POL-CORRUPTO' == 'POL-2026-ABC02'
FAILED tests/test_ia_corregido.py::test_primas_variadas_son_aceptadas - AssertionError: assert 'POL-CORRUPTO' == 'POL-2026-VAR00'
2 failed, 4 passed, 1 warning in 2.97s
```

- **Corrección:** En tests/test_ia_corregido.py, se reemplazó el MagicMock por una base de datos SQLite en memoria (sqlite:// con StaticPool) inyectada mediante app.dependency_overrides. Además, se añadieron validaciones del contenido de la respuesta (como el número de póliza) para detectar datos corruptos.

```python
# Corrección en tests/test_ia_corregido.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import get_db, Base

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
```

## Defecto 3

- **Qué está mal:** El test original genera sus datos con `uuid.uuid4()` y con `random.choice` / `random.uniform` sin semilla. Cada ejecución prueba valores distintos y no reproducibles, y ninguna aserción depende de ellos: solo comprueba que exista la clave `puntaje`, no su valor. Un servicio que devuelva datos aleatorios pasa igual.
- **Por qué es un defecto** (M10 · 7. Reproducibilidad sin Docker): Un test debe ser determinista y reproducible: si falla, hay que poder repetir el fallo con los mismos datos. Con datos sin semilla es imposible, y además el test no fija el resultado esperado, así que no puede fallar cuando el código está mal.
- **Cómo lo comprobamos:**

# mutación
```diff
# Mutación: en main.py
+ import random

  # dentro de puntuar():
-     puntaje = float(modelo.predict_proba(rasgos)[0][1])
+     puntaje = random.uniform(0, 0.5)  # mutación: puntaje aleatorio sin semilla
```
# test original, en verde
```python
# Salida de pytest con el test ORIGINAL sobre el servicio mutado
codigo de evidencia: python -m pytest ia_tests_propuesta.py -v

6 passed, 1 warning
```
# test corregido, en rojo
```python
# Salida de pytest con el test CORREGIDO sobre el servicio mutado
codigo de evidencia: python -m pytest tests/test_ia_corregido.py

def test_score_de_poliza_recien_creada():
        datos = _poliza()
        assert cliente.post("/polizas", json=datos).status_code == 201
        r = cliente.post("/score", json={"numero": datos["numero"]})
        assert r.status_code == 200
>       assert r.json()["puntaje"] == 0.8
E       assert 0.2949 == 0.8

tests\test_ia_corregido.py:118: AssertionError

FAILED tests/test_ia_corregido.py::test_score_de_poliza_recien_creada - assert 0.2949 == 0.8
1 failed, 5 passed, 1 warning in 2.78s
```

- **Corrección:** Datos deterministas y valor esperado fijo. Se eliminó `uuid`. Se usa una única instancia `random.Random(42)` a nivel de módulo. Las primas variadas pasan a ser explícitas con `@pytest.mark.parametrize`, con un número de póliza distinto por caso. El modelo real se sustituye por un `ModeloFalso` que siempre devuelve 0.8 (vía `dependency_overrides[cargar_modelo]`), y el test comprueba `r.json()["puntaje"] == 0.8`.

```python
class ModeloFalso:
    def predict_proba(self, rasgos):
        return [[0.2, 0.8] for _ in rasgos]

app.dependency_overrides[cargar_modelo] = lambda: ModeloFalso()
_RNG = random.Random(42)

PRIMAS = [(0, 1.0), (1, 99.99), (2, 123_456.78), (3, 1_500_000.5), (4, 5_000_000.0)]

@pytest.mark.parametrize("i, prima", PRIMAS)
def test_primas_variadas_son_aceptadas(i, prima):
    datos = _poliza(numero=f"POL-2026-VAR{i:02d}", prima=prima)
    ...

# en test_score_de_poliza_recien_creada
assert r.json()["puntaje"] == 0.8
```
