from app import create_app
from app.database.seed import seed_database

app = create_app()
with app.app_context():
    seed_database()
    
#! If you need to seed the database make sure you delete the tables first

# -- Truncate all tables (keeps tables but removes all data)
# TRUNCATE TABLE appointments;
# TRUNCATE TABLE prescriptions;
# TRUNCATE TABLE test_results;
# TRUNCATE TABLE patient_login;
# TRUNCATE TABLE doctor_login;
# TRUNCATE TABLE admin_login;
# TRUNCATE TABLE patients;
# TRUNCATE TABLE doctors;
# TRUNCATE TABLE user_login;

# -- Re-enable foreign key checks
# SET FOREIGN_KEY_CHECKS = 1;

#! Use MySQL workbench to run this code