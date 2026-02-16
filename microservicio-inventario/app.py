import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from modelos import db, Inventario
from apscheduler.schedulers.background import BackgroundScheduler
from tasks import poll_reservations

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

    return app

app = create_flask_app()
db.init_app(app)

with app.app_context():
    db.create_all()
    # Seed initial inventory if empty
    if not Inventario.query.first():
        db.session.add(Inventario(producto='Habitacion_Standard', cantidad=100))
        db.session.commit()

# Scheduler setup
scheduler = BackgroundScheduler()
# Run polling every 10 seconds as per H1
scheduler.add_job(lambda: app.app_context().push() or poll_reservations(), 'interval', seconds=10)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5004)), debug=False, use_reloader=False)
