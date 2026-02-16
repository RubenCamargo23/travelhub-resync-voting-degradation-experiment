from flask import request
from flask_restful import Resource
from modelos import db, Reserva, ReservationEvent
import json

class VistaReservas(Resource):
    """
    IMPLEMENTACIÓN DEL PATRÓN OUTBOX (H1: Eventual Consistency)
    
    Esta vista maneja la creación de reservas aplicando el principio de "Dual Write" seguro.
    En lugar de llamar síncronamente al servicio de Inventario (que podría estar caído),
    guardamos un "Evento de Dominio" en nuestra propia base de datos, en la misma transacción.
    
    Beneficios:
    1.  Disponibilidad: Si Inventario se cae, Reservas sigue funcionando (201 Created).
    2.  Atomicidad: La reserva y el evento se guardan o fallan juntos.
    3.  Recuperación: El evento pendiente permite que Inventario se sincronice luego (Polling).
    
    PARA PROBAR ESTA TÁCTICA:
    1. Asegurar que Reservas está corriendo.
    2. Detener `microservicio-inventario`.
    3. En el Frontend, crear una Reserva (POST /reservas).
       - ÉXITO: Recibe 201 Created inmediatamente.
       - La reserva se guarda en DB local + Evento 'RESERVATION_CREATED' en tabla `reservation_events`.
    4. Reiniciar `microservicio-inventario`.
    5. Observar logs de Inventario:
       - Detectará eventos pendientes y los procesará ("Found X pending events").
       - Actualizará su stock local.
    """
    def post(self):
        try:
            data = request.get_json()
            
            # ---------------------------------------------------------------------
            # PASO 1: TRANSACCIÓN LOCAL (Reserva)
            # Guardamos la entidad principal.
            # ---------------------------------------------------------------------
            nueva_reserva = Reserva(
                cliente=data.get('cliente', 'Anonimo'),
                monto=data.get('monto', 0.0)
            )
            db.session.add(nueva_reserva)
            db.session.flush() # Para obtener ID
            
            # ---------------------------------------------------------------------
            # PASO 2: CREACIÓN DEL EVENTO DE DOMINIO (Outbox)
            # Creamos un registro 'ReservationEvent' con estado inicial 'procesado = NULL'.
            # Esto actúa como cola de mensajes persistente dentro de la misma DB.
            # ---------------------------------------------------------------------
            evento = ReservationEvent(
                event_type='RESERVATION_CREATED',
                reservation_id=nueva_reserva.id,
                payload=json.dumps(data)
            )
            db.session.add(evento)
            
            # ---------------------------------------------------------------------
            # PASO 3: COMMIT ATÓMICO
            # Ambas operaciones (Reserva + Evento) se confirman al tiempo.
            # ---------------------------------------------------------------------
            db.session.commit()
            
            return {
                "mensaje": "Reserva creada exitosamente (Evento pendiente de sync)",
                "id": nueva_reserva.id,
                "evento_id": evento.id,
                "nota": "El inventario se actualizará asíncronamente"
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class VistaReserva(Resource):
    def get(self, id_reserva):
        return {"mensaje": "Detalle reserva"}

import requests
from collections import Counter
import concurrent.futures

class VistaPagoReserva(Resource):
    """
    IMPLEMENTACIÓN DEL PATRÓN DE CONSENSO (N-VERSION PROGRAMMING)
    
    Esta vista orquesta el pago distribuyéndolo entre múltiples réplicas del servicio de Pagos.
    El objetivo es tolerar fallos bizantinos (datos corruptos/erróneos) en una o más réplicas
    mediante un sistema de votación por mayoría simple.
    
    Flujo:
    1.  Scatter: Envía la misma petición a N réplicas en paralelo.
    2.  Gather: Recolecta respuestas, descartando fallos de conexión (timeouts/500).
    3.  Vote: Agrupa respuestas idénticas.
    4.  Decide: Si una respuesta tiene > 50% de los votos, se acepta como la "verdad".

    PARA PROBAR ESTA TÁCTICA:
    1. El sistema simula 5 réplicas de pagos (IDs 1-5).
    2. La réplica #5 está programada para fallar (retorna valor x10).
    3. En el Frontend, clic en 'Pagar Reserva (Consenso)'.
       - El sistema hace Fan-Out (5 peticiones paralelas).
    4. Observar la respuesta:
       - ÉXITO: "Pago Exitoso (Consenso)".
       - El algoritmo de votación descartó la respuesta errónea de la réplica 5.
       - Se confirma que la mayoría (4 vs 1) coincidió en el valor correcto.
    """
    def post(self, id_reserva):
        # URL del servicio de pagos (Orquestador llama a Pagos)
        PAYMENTS_URL = "http://127.0.0.1:5003/pago"
        
        # Simular 5 replicas llamando al mismo servicio con diferente ID
        # En producción, serían 5 URLs/IPs distintas.
        param_list = [{"replica_id": i, "amount": 45.0} for i in range(1, 6)]
        
        results = []
        
        def call_replica(params):
            """Función auxiliar para llamar a una réplica individual con timeout."""
            try:
                resp = requests.post(PAYMENTS_URL, json=params, timeout=2)
                if resp.status_code == 200:
                    return resp.json()['processed_amount']
            except:
                return None
            return None

        # ---------------------------------------------------------------------
        # PASO 1: EJECUCIÓN PARALELA (FAN-OUT)
        # Usamos hilos para no bloquear el proceso esperando a cada réplica secuencialmente.
        # Si una réplica es lenta, no afecta el tiempo total de las demás.
        # ---------------------------------------------------------------------
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(call_replica, param_list))
        
        # ---------------------------------------------------------------------
        # PASO 2: FILTRADO DE FALLOS
        # Ignoramos réplicas que no respondieron (None) o dieron error 500.
        # Solo votan las que están vivas.
        # ---------------------------------------------------------------------
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            return {"error": "Payment failed completely (0 replicas available)"}, 500
            
        # ---------------------------------------------------------------------
        # PASO 3: CONTEO DE VOTOS
        # Agrupamos las respuestas idénticas.
        # Ej: {45.0: 4 votos, 450.0: 1 voto}
        # ---------------------------------------------------------------------
        counts = Counter(valid_results)
        most_common_amount, votes = counts.most_common(1)[0]
        
        # ---------------------------------------------------------------------
        # PASO 4: REGLA DE MAYORÍA (CONSENSO)
        # Para N=5, la mayoría simple es 3 (5 // 2 + 1).
        # Si la opción ganadora no alcanza este umbral, el sistema no confía.
        # ---------------------------------------------------------------------
        if votes >= 3:
            return {
                "mensaje": "Pago Exitoso (Consenso)",
                "monto_acordado": most_common_amount,
                "votos": votes,
                "distribucion_votos": dict(counts)
            }, 200
        else:
            return {
                "error": "Consenso fallido (No majority agreement)",
                "distribucion_votos": dict(counts)
            }, 409
