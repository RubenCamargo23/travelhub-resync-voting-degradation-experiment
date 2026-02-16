from flask import request
from flask_restful import Resource
from modelos import db, PaymentVote

class VistaPago(Resource):
    def post(self):
        data = request.get_json()
        replica_id = data.get('replica_id', 1)
        base_amount = data.get('amount', 45.0)
        
        # Simulación de BUG en Réplica 5
        final_amount = base_amount
        if int(replica_id) == 5:
            final_amount = base_amount * 10 # Retorna $450 en vez de $45
            
        # Registrar voto
        vote = PaymentVote(replica_id=replica_id, amount=final_amount)
        db.session.add(vote)
        db.session.commit()
        
        return {
            "mensaje": "Pago procesado",
            "replica_id": replica_id,
            "processed_amount": final_amount,
            "status": "success"
        }, 200
