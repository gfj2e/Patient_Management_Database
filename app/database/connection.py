# from flask_sqlalchemy import SQLAlchemy
# from google.cloud.sql.connector import Connector
# import os
# from dotenv import load_dotenv
# load_dotenv()

# connector = Connector()

# db = SQLAlchemy()

# # Connects to a local MySQL server using SQLAlchemy server connector
# # Use your own login credentials to connect to your server
# # def init_connection_engine(app):
# #     db_user = "root"                # Replace these credentials
# #     db_password = "password"
# #     # db_password = "andy"
# #     db_name = "patient_mgmt"
# #     db_host = "localhost"

# #     # app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
# #     # app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Hien2003!!@127.0.0.1:3306/patient_mgmt"
# #     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
# #     db.init_app(app)
    
# #     with app.app_context():
# #         try:
# #             db.engine.connect()
# #             print("Database connection successful!")
# #             app.config['DB_CONNECTED'] = True
# #             return app  
# #         except Exception as e:
# #             print(f"Failed to connect to database: {str(e)}")
# #             app.config['DB_CONNECTED'] = False
# #             return app  







# INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
# DB_USER = os.getenv("DB_USER")
# DB_PASS = os.getenv("DB_PASS")
# DB_NAME = os.getenv("DB_NAME")
        
# def init_connection_engine(app):
#         app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://"
#         app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
#         "creator": lambda: connector.connect(
#             INSTANCE_CONNECTION_NAME,
#             "pymysql",
#             user=DB_USER,
#             password=DB_PASS,
#             db=DB_NAME,
#             ip_type="public"
#         )
#     }
#         app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#         db.init_app(app)

#         print("Database engine initialized successfully.")
#         # return app






from flask_sqlalchemy import SQLAlchemy
from google.cloud.sql.connector import Connector
import os
from dotenv import load_dotenv

# Load .env file variables
load_dotenv()

# Initialize Google Cloud connector and SQLAlchemy
connector = Connector()
db = SQLAlchemy()

# Environment variables from .env
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "patient_mgmt")

#SET USE_CLOUD TO FALSE TO USE LOCAL CONNECTION
USE_CLOUD = os.getenv("USE_CLOUD", "false").lower() == "true"

def init_connection_engine(app):
    if USE_CLOUD:
        print("Using Google Cloud SQL connection...")
        app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://"
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "creator": lambda: connector.connect(
                INSTANCE_CONNECTION_NAME,
                "pymysql",
                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME,
                ip_type="public"
            )
        }
    else:
        print("Using local MySQL connection...")
        #UNCOMMENT YOUR LOCAL CONNECTION BELOW

        # karigan local
        # app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:password@localhost/patient_mgmt"
        # anlee local
        # app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Hien2003!!@127.0.0.1:3306/patient_mgmt"
        # heather local
        app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@127.0.0.1:3306/patient_mgmt"



    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Bind SQLAlchemy to Flask app
    db.init_app(app)

    print("Database engine initialized successfully.")
