from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
# from google.cloud.sql.connector import Connector
# connector = Connector()
load_dotenv()
db = SQLAlchemy()

# Connects to a local MySQL server using SQLAlchemy server connector
# Use your own login credentials to connect to your server
def init_connection_engine(app):
    db_user = os.getenv("DB_USER")              # Replace these credentials
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST")

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    # app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Hien2003!!@127.0.0.1:3306/patient_mgmt"
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









# from flask_sqlalchemy import SQLAlchemy
# import os
# from dotenv import load_dotenv

# # Load .env file variables
# load_dotenv()

# db = SQLAlchemy()

# # Environment variables
# INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
# DB_USER = os.getenv("DB_USER", "root")
# DB_PASS = os.getenv("DB_PASS", "")
# DB_NAME = os.getenv("DB_NAME", "patient_mgmt")

# # Toggle for cloud vs local connection
# USE_CLOUD = os.getenv("USE_CLOUD", "false").lower() == "true"

# def init_connection_engine(app):
#     """
#     Initializes the SQLAlchemy engine using either:
#     - Google Cloud SQL Connector (if USE_CLOUD=true)
#     - Local MySQL (if USE_CLOUD=false)
#     """
#     if USE_CLOUD:
#         print("Using Google Cloud SQL connection...")
#         from google.cloud.sql.connector import Connector  # import only if needed
#         connector = Connector()

#         app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://"
#         app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
#             "creator": lambda: connector.connect(
#                 INSTANCE_CONNECTION_NAME,
#                 "pymysql",
#                 user=DB_USER,
#                 password=DB_PASS,
#                 db=DB_NAME,
#                 ip_type="public"
#             )
#         }
#     else:
#         print("Using local MySQL connection...")
#         # Heather’s local setup
#         app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@127.0.0.1:3306/{DB_NAME}"

#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#     db.init_app(app)
#     print("Database engine initialized successfully.")