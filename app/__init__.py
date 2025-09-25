from flask import Flask
from .main.routes import main_bp 
from .auth.routes import auth_bp
from .patient.routes import patient_bp
from .database.connection import init_connection_engine, db
from .database.models import *
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.secret_key = "your_secret_key"
    
    app = init_connection_engine(app)
    
    with app.app_context():
        db.create_all() 
    
    migrate.init_app(app, db)
    
    # register the blueprints with app 
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    return app