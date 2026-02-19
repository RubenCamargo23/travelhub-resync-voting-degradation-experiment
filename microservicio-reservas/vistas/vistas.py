from flask import request
from flask_restful import Resource
from modelos import db, Reserva
import requests

class VistaReservas(Resource):
    """
    Versión SIN tácticas de disponibilidad.
    Guarda la reserva directamente sin Outbox/Event Log.
    """
    def post(self):
        try:
            data = request.get_json()

            nueva_reserva = Reserva(
                cliente=data.get('cliente', 'Anonimo'),
                monto=data.get('monto', 0.0)
            )
            db.session.add(nueva_reserva)
            db.session.commit()

            return {
                "mensaje": "Reserva creada exitosamente",
                "id": nueva_reserva.id
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class VistaReserva(Resource):
    def get(self, id_reserva):
        return {"mensaje": "Detalle reserva"}


class VistaPagoReserva(Resource):
    """
    Versión SIN tácticas de disponibilidad.
    Llama al servicio de pagos una sola vez (sin réplicas ni votación).
    """
    def post(self, id_reserva):
        PAYMENTS_URL = "http://127.0.0.1:5003/pago"

        try:
            resp = requests.post(PAYMENTS_URL, json={"replica_id": 1, "amount": 45.0}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "mensaje": "Pago procesado",
                    "monto": data.get("processed_amount")
                }, 200
            else:
                return {"error": "Payment service returned an error"}, resp.status_code
        except Exception as e:
            return {"error": str(e)}, 503
