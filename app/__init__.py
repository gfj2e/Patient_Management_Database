from flask import Flask
from .main.routes import main_bp 
from .auth.routes import auth_bp
from .database.connection import init_connection_engine, db
from .database.models import *

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.secret_key = "your_secret_key"
    
    app = init_connection_engine(app)
    
    with app.app_context():
        if app.config.get('DB_CONNECTED'):
            db.create_all()
            print("Database tables created successfully!")
        else:
            print("Warning: Database not connected, skipping create_all().")
    
    # register the blueprints with app 
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    return app