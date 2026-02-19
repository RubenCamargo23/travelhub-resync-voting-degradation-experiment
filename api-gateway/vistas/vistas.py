from flask_restful import Resource
from circuitbreaker import circuit
import requests
import datetime

# Configuración del Circuit Breaker
# Se abre tras 3 fallos seguidos. Tiempo de recuperación 30s.
FAIL_THRESHOLD = 3
RECOVERY_TIMEOUT = 30

def fallback_search():
    return {
        "mensaje": "Servicio de búsqueda no disponible temporalmente. Resultados cacheados/limitados.",
        "origen": "Fallback (Circuit Breaker Abierto)",
        "timestamp": str(datetime.datetime.now())
    }, 200

"""
HIPÓTESIS 3: CIRCUIT BREAKER / DEGRADACIÓN FUNCIONAL
---------------------------------------------------
Para probar esta táctica:
1. Asegurar que el sistema corre (scripts/start_backend.sh).
2. Verificar funcionamiento normal: GET /search -> responde 200 OK con datos.
3. INYECTAR FALLO: Matar el proceso de `microservicio-busqueda` (puerto 5001).
   $ lsof -i :5001 -> obtener PID -> kill -9 <PID>
4. Intentar buscar nuevamente (3 veces).
   - Fallos 1-3: responderán con error 500/Timeout. El CB cuenta fallos.
5. Intento 4 (Circuit Breaker Abierto):
   - Responderá INMEDIATAMENTE con el JSON de abajo (Fallback).
   - "origen": "Fallback (Circuit Breaker Abierto)"
   - ÉXITO: El sistema se degradó funcionalmente en lugar de fallar.
6. RECUPERACIÓN:
   - Reiniciar `microservicio-busqueda`.
   - Esperar 30s (RECOVERY_TIMEOUT).
   - El siguiente intento cerrará el circuito y funcionará normal.
"""

# Decorador
@circuit(failure_threshold=FAIL_THRESHOLD, recovery_timeout=RECOVERY_TIMEOUT, fallback_function=fallback_search)
def external_search():
    # URL del Microservicio Búsqueda
    # Si falla (ConnectionError, 500, timeout), lanza excepción y cuenta para el CB
    url = "http://127.0.0.1:5001/busqueda"
    response = requests.get(url, timeout=2)
    if response.status_code >= 500:
        raise Exception("Server Error")
    return response.json(), response.status_code

class VistaBusquedaGateway(Resource):
    def get(self):
        try:
            return external_search()
        except Exception as e:
            # Si el CB está cerrado pero falla la llamada (y no saltó al fallback del decorador por alguna razón)
            return {"error": str(e)}, 503


# =============================================================================
# VERSIÓN NAIVE (SIN TÁCTICAS) — Para contraste experimental
# =============================================================================

class VistaBusquedaGatewayNaive(Resource):
    """
    SIN Circuit Breaker. Llama directamente al microservicio de búsqueda.
    Si el servicio está caído, cada intento falla con error directo (sin fallback ni protección).
    """
    def get(self):
        try:
            url = "http://127.0.0.1:5001/busqueda"
            response = requests.get(url, timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e), "tactica": "ninguna"}, 503

