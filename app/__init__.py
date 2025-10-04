from flask import Flask
from .main.routes import main_bp 
from .auth.routes import auth_bp
from .patient.routes import patient_bp
from .doctor.routes import doctor_bp
from .database.connection import init_connection_engine, db
from .database.models import User_Login
from flask_migrate import Migrate
from .extensions import bcrypt, login_manager

migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.secret_key = "your_secret_key"
    
    app = init_connection_engine(app)
    
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User_Login.query.get(int(user_id))
    
    with app.app_context():
        db.create_all() 
    
    migrate.init_app(app, db)
    
    # register the blueprints with app 
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    return app