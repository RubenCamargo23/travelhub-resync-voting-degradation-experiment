import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from modelos import db
from vistas import VistaReservas, VistaReserva, VistaPagoReserva

def create_flask_app():
    app = Flask(__name__)
    
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///db.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "frase-secreta")
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_IDENTITY_CLAIM"] = "sub"

    CORS(app, resources={r"/*": {"origins": "*"}})
    
    api = Api(app)
    api.add_resource(VistaReservas, '/reservas')
    api.add_resource(VistaReserva, '/reservas/<int:id_reserva>')
    api.add_resource(VistaPagoReserva, '/reservas/<int:id_reserva>/pagar')
    
    jwt = JWTManager(app)

    return app

app = create_flask_app()
db.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5002)), debug=False)
