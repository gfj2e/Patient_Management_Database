from flask import Flask
from .main.routes import main_bp 
from .auth.routes import auth_bp

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.secret_key = "your_secret_key"
    # register the blueprints with app 
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    return app