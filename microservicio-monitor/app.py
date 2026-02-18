
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api, Resource
from modelos import db
from apscheduler.schedulers.background import BackgroundScheduler
import requests

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
    
    jwt = JWTManager(app)

    return app, api

app, api = create_flask_app()
db.init_app(app)

class HealthCheck(Resource):
    def get(self):
        services = {
            "reservas": "http://127.0.0.1:5002/reservas",
            "pagos": "http://127.0.0.1:5003/pago", # Assuming root or similar exists, or just port check
            "inventario": "http://127.0.0.1:5004", # Inventario root
            "busqueda": "http://127.0.0.1:5001/busqueda",
            "gateway": "http://127.0.0.1:5007/search", # Gateway check
            "monitor": "http://127.0.0.1:5006" # Self
        }
        
        status_report = {}
        
        for name, url in services.items():
            if name == "monitor":
                status_report[name] = "online"
                continue
                
            try:
                # Short timeout to detect failures quickly
                response = requests.get(url, timeout=1)
                # Any response (even 404 or 401) means the service is alive/reachable at network level
                # For this experiment, connectivity = online.
                # If we want functional check, we'd check 200 OK.
                # However, some endpoints need auth or valid data.
                # A connection error means offline.
                status_report[name] = "online"
            except requests.exceptions.RequestException:
                status_report[name] = "offline"

        return jsonify(status_report)

api.add_resource(HealthCheck, '/health-check')

# Scheduler setup
scheduler = BackgroundScheduler()
# scheduler.add_job(func, 'interval', seconds=60)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5006)), debug=False)
