from flask_restful import Resource
import time
import random

class VistaBusqueda(Resource):
    def get(self):
        # Simular latencia variable
        time.sleep(random.uniform(0.1, 0.5))
        return [
            {"id": 1, "nombre": "Hotel Playa", "precio": 100},
            {"id": 2, "nombre": "Hotel Montaña", "precio": 80}
        ], 200
