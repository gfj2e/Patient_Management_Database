# from flask_sqlalchemy import SQLAlchemy
# from google.cloud.sql.connector import Connector

# connector = Connector()

# db = SQLAlchemy()

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
    
#     db.init_app(app)
    
#     with app.app_context():
#         try:
#             db.engine.connect()
#             app.logger.info("Successfully connected to database!")
#             print("Database connection successful!")
#             return db
#         except Exception as e:
#             app.logger.error(f"Database connection error: {str(e)}")
#             print(f"Failed to connect to database: {str(e)}")
#             return db