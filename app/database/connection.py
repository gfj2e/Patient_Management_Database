from flask_sqlalchemy import SQLAlchemy
# from google.cloud.sql.connector import Connector

# connector = Connector()

db = SQLAlchemy()

db_user = "root"
db_password = "Gfj2e_7719"
db_password = "andy"
db_name = "patient_mgmt"
db_host = "localhost"

def init_connection_engine(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.engine.connect()
            print("Database connection successful!")
            app.config['DB_CONNECTED'] = True
            return app  
        except Exception as e:
            print(f"Failed to connect to database: {str(e)}")
            app.config['DB_CONNECTED'] = False
            return app  
        
    # def init_connection_engine(app):
#     app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://"
#     app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
#         "creator": lambda: connector.connect(
#             "indigo-idea-472512-b0:us-east1:patient-mgmt",
#             "pymysql",
#             user = "root",
#             password="Database_mgmt4560",
#             db = "patient_mgmt",
#             ip_type = "public"
#         ),
#     }
    