from flask_restful import Resource
import requests


class VistaBusquedaGateway(Resource):
    """
    Versión SIN tácticas de disponibilidad.
    Llama directamente al microservicio de búsqueda sin Circuit Breaker ni fallback.
    """
    def get(self):
        try:
            url = "http://127.0.0.1:5001/busqueda"
            response = requests.get(url, timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e)}, 503
