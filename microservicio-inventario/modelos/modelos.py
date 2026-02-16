from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Inventario(db.Model):
    __tablename__ = 'inventario'
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
