import os
from sqlalchemy import create_engine, text
from modelos import db, Inventario
from datetime import datetime

# Definir la URL de la DB de Reservas (Para el experimento local, apuntamos al archivo o servicio)
# En un entorno real, esto sería una variable de entorno apuntando a la DB de Reservas
basedir = os.path.abspath(os.path.dirname(__file__))
# Asumimos estructura: parent/microservicio-inventario/tasks.py, db está en parent/microservicio-reservas/instance/db.sqlite o parent/microservicio-reservas/db.sqlite
# Flask-SQLAlchemy 3+ pone db en instance/ por defecto, pero aquí lo configuramos manual en app.py como "sqlite:///db.sqlite" (relative to app.py working dir)
reservas_db_path = os.path.join(basedir, '..', 'microservicio-reservas', 'instance', 'db.sqlite') 
# Sin embargo, app.py de reservas usa "sqlite:///db.sqlite", que suele crearse en el root carpeta si no se especifica.
reservas_db_path_v1 = os.path.join(basedir, '..', 'microservicio-reservas', 'db.sqlite')

# Probamos V1 porque en app.py no se ve 'instance' y Flask<3 lo ponía en root.
# Probamos V1 porque en app.py no se ve 'instance' y Flask<3 lo ponía en root.
# Probamos V1 porque en app.py no se ve 'instance' y Flask<3 lo ponía en root.
RESERVAS_DB_URL = os.environ.get("RESERVAS_DB_URL", f"sqlite:///{reservas_db_path}")

def poll_reservations():
    """
    IMPLEMENTACIÓN DE POLLING CONSUMER (H1: Eventual Consistency)
    
    Esta función se ejecuta periódicamente (scheduler) para sincronizar estado.
    Actúa como un "Worker" que procesa mensajes de la 'Outbox' de Reservas.
    
    Flujo:
    1.  Pull: Conecta a la DB de Reservas y busca eventos NO procesados (processed_at IS NULL).
    2.  Process: Por cada evento, actualiza el inventario local (Idempotencia requerida).
    3.  Ack: Marca el evento como procesado en la DB de Reservas para no repetirlo.
    """
    print(f"[{datetime.now()}] Polling events from Reservations DB...")
    
    # ---------------------------------------------------------------------
    # PASO 1: LECTURA DE EVENTOS (PULL)
    # Buscamos en la 'Cola' (Tabla reservation_events) todo lo pendiente.
    # ---------------------------------------------------------------------
    try:
        engine = create_engine(RESERVAS_DB_URL)
        with engine.connect() as connection:
            # Seleccionamos solo eventos que nadie más ha procesado
            query = text("SELECT id, event_type, payload FROM reservation_events WHERE processed_at IS NULL ORDER BY created_at ASC")
            result = connection.execute(query)
            events = result.fetchall()
            
            if not events:
                print("No pending events found.")
                return

            print(f"Found {len(events)} pending events.")
            
            # ---------------------------------------------------------------------
            # PASO 2: PROCESAMIENTO E IDEMPOTENCIA
            # Iteramos sobre cada mensaje para aplicar el cambio de estado local.
            # ---------------------------------------------------------------------
            for event in events:
                event_id, event_type, payload = event
                print(f"Processing event {event_id}: {event_type}")
                
                # Simulación de lógica de negocio: Restar inventario
                # En un caso real, la operación debe ser idempotente (si procesamos el mismo id 2 veces, no restart 2 veces)
                
                # Ejemplo: Restar 1 al inventario global 'Habitaciones'
                item = Inventario.query.filter_by(producto='Habitacion_Standard').first()
                if not item:
                    item = Inventario(producto='Habitacion_Standard', cantidad=100)
                    db.session.add(item)
                
                if item.cantidad > 0:
                    item.cantidad -= 1
                    db.session.add(item)
                
                # ---------------------------------------------------------------------
                # PASO 3: CONFIRMACIÓN (ACK)
                # Marcamos el evento en la fuente como completado.
                # Esto saca el mensaje de la 'Cola'.
                # ---------------------------------------------------------------------
                update_query = text("UPDATE reservation_events SET processed_at = :now WHERE id = :id")
                connection.execute(update_query, {"now": datetime.now(), "id": event_id})
                connection.commit()
            
            # Commit local changes
            db.session.commit()
            print("Sync completed successfully.")
            
    except Exception as e:
        print(f"Error polling reservations: {e}")
        db.session.rollback()
