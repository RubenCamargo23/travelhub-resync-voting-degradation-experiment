from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()

class PaymentVote(db.Model):
    __tablename__ = 'payment_votes'
    id = db.Column(db.Integer, primary_key=True)
    replica_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=dt.datetime.now)
