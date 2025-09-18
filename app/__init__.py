from flask import Flask
from .main.routes import main_bp 
from .auth.routes import auth_bp
from .database.connection import init_connection_engine, db

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.secret_key = "your_secret_key"
    
    init_connection_engine(app)
    
    # register the blueprints with app 
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    return app