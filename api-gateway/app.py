import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from modelos import db
from vistas import VistaBusquedaGateway, VistaBusquedaGatewayNaive

def create_flask_app():
    app = Flask(__name__)
    
    # Database config
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
    api.add_resource(VistaBusquedaGateway, '/search')
    # Naive endpoint (sin tácticas)
    api.add_resource(VistaBusquedaGatewayNaive, '/search/naive')
    
    jwt = JWTManager(app)

    return app

app = create_flask_app()
db.init_app(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5007)), debug=False)
