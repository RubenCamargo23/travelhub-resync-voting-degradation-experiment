from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import datetime as dt

db = SQLAlchemy()

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_reserva = db.Column(db.DateTime, default=dt.datetime.now)
    cliente = db.Column(db.String(100))
    monto = db.Column(db.Float)

class ReservationEvent(db.Model):
    __tablename__ = 'reservation_events'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50)) # 'CREATED', 'CANCELLED'
    reservation_id = db.Column(db.Integer)
    payload = db.Column(db.String(500)) # JSON string
    created_at = db.Column(db.DateTime, default=dt.datetime.now)
    processed_at = db.Column(db.DateTime, nullable=True) # Para control, aunque Inventario maneja su propio cursor idealmente
