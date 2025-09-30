from ..database.models import *
from ..database.connection import db
from faker import Faker
from datetime import date, datetime, timedelta
import uuid
import random
import string

# Purpose of this file is to generate fake data to fill the database with information
# for testing purposes. Uses the Faker library to fufill this

Faker.seed(0)
fake = Faker()

SPECIALTIES = ("Family Medicine", "Cardiology", "Pediatrics", "Neurology",
               "Orthopedics", "Dermatology", "Gynecology", "Oncology")

# Function to generate a phone number in the format of (XXX) XXX-XXXX
def generate_phone_number() -> int:
    number = "("
    
    area_code = random.randint(200, 999)
    number += str(area_code) + ") "
    
    sub1 = ''.join(str(random.randint(0, 9)) for i in range(3))
    
    number += sub1 + "-"
    
    sub2 = ''.join(str(random.randint(0, 9)) for i in range(4))
    number += sub2
    
    return number

# Function that will automatically calculate the age based on a datetime variable passed through
# the function
def calculate_age(dob) -> str:
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

# Seed the database with the fake data
def seed_database() -> None:
    # destructive: drop existing tables and recreate schema so seeding is idempotent
    print("Seeding database with data...")
    db.drop_all()
    db.create_all()
    
    doctors = []
    
    # Create 10 doctors
    # ensure Faker will produce unique values for emails to avoid unique-key collisions
    fake.unique.clear()
    for i in range(10):
        doctor = Doctor(
            first_name = fake.first_name(),
            last_name = fake.last_name(),
            specialty = random.choice(SPECIALTIES),
            state = fake.state(),
            city = fake.city(),
            phone_number = generate_phone_number(),
            email = fake.unique.email(),
            is_accepting_new_patients = random.choice([True, False])
        )
        doctors.append(doctor)
    db.session.add_all(doctors)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        # If something odd happens, try to insert doctors individually to get clearer errors
        for d in doctors:
            try:
                db.session.add(d)
                db.session.commit()
            except Exception:
                db.session.rollback()
                # skip problematic doctor
                continue
    
    patients = []
    
    # Create 50 patients
    # reset unique provider for patient emails
    fake.unique.clear()
    for i in range(50):
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=100)
        patient = Patient(
            patient_code = str(uuid.uuid4())[:16],
            first_name = fake.first_name(),
            last_name = fake.last_name(),
            dob = date_of_birth,
            age = calculate_age(date_of_birth),
            address = fake.address().replace('\n', ', '),
            phone_number = generate_phone_number(),
            email = fake.unique.email(),
            gender = random.choice(list(Gender)),
            height = str(random.uniform(150.0, 200.0)),
            marriage_status = random.choice(list(MaritalStatus)),
            race = random.choice(list(Race)),
            insurance_id = f"INS{fake.random_number(digits=8)}",
            doctor_id = random.choice(doctors).doctor_id
        )
        patients.append(patient)
    db.session.add_all(patients)
    db.session.commit()
    
    # Patient with id 1 will be assigned the fake data with prescriptions, test_results,
    # and appointments
    insert_test_data(patients[0].patient_id, patients[0].doctor_id)
    
    # The doctors and patients are also to be linked to user accounts for them
    doctor_logins = []
    for doctor in doctors:
        doctor_login = Doctor_Login(    
            user_name = f"{doctor.first_name.lower()}.{doctor.last_name.lower()}",
            email = doctor.email,
            password = ''.join(random.sample(string.ascii_lowercase, 8)),
            doctor_id = doctor.doctor_id,
            type = "doctor_login"
        )
        
        doctor_logins.append(doctor_login)
    db.session.add_all(doctor_logins)
    db.session.commit()
    
    patient_logins = []
    for patient in patients:
        patient_login = Patient_Login(
            user_name = f"{patient.first_name.lower()}.{patient.last_name.lower()}",
            email = patient.email,
            password = ''.join(random.sample(string.ascii_lowercase, 8)),
            patient_id = patient.patient_id,
            type = "patient_login"
        )
        patient_logins.append(patient_login)
    db.session.add_all(patient_logins)
    db.session.commit()
    
    # Only one admin_login required
    admin = Admin_Login(
        user_name = "admin",
        email = "admin@garrettisgreat.com",
        password = "garrett_is_awesome",
        type = "admin_login"
    )
    db.session.add(admin)
    db.session.commit()
    
    print("Database seeding complete!")
    
def insert_test_data(patient_ident: int, doctor_ident: int) -> None:
    prescriptions = [
        Prescription(
            medication_name = "Lisinopril",
            dosage = "10mg",
            frequency_taken = "Once daily in the morning",
            notes = "For blood pressure control. Take with or without food.",
            patient_id = patient_ident,
            doctor_id = doctor_ident
        ),
        Prescription(
          medication_name = "Atorvastatin",
          dosage = "20mg",
          frequency_taken = "Once daily at bedtime",
          notes = "For cholesterol management. Avoid grapefruit juice.",
          patient_id = patient_ident,
          doctor_id = doctor_ident
        ),
        Prescription(
            medication_name = "Metformin",
            dosage = "500mg",
            frequency_taken = "Twice daily with meals",
            notes = "For diabetes management",
            patient_id = patient_ident,
            doctor_id = doctor_ident
        )
    ]
    db.session.add_all(prescriptions)
    db.session.commit()
    
    appointments = [
        Appointment(
            appointment_time = datetime.now() + timedelta(days=14),
            clinic_name = "Ohio Medical Center",
            state = "Ohio",
            city = "Lauration",
            patient_id = patient_ident,
            doctor_id = doctor_ident
        )
    ]
    db.session.add_all(appointments)
    db.session.commit()
    
    test_results = [
        Test_Result(
            test_name = "Complete Blood Couint",
            test_status = TestStatus.COMPLETED,
            ordered_date = datetime.now() - timedelta(days=45),
            result_time = datetime.now() - timedelta(days=42),
            result_value="WBC: 6.5, RBC: 4.2, Hgb: 12.8, Plt: 240",
            unit_of_measure="K/uL, M/uL, g/dL, K/uL",
            reference_range="WBC: 4.5-11.0, RBC: 4.0-5.2, Hgb: 12.0-16.0, Plt: 150-450",
            is_abnormal = False,
            result_notes="Results within normal limits",
            patient_id=1
        ),
        Test_Result(
            test_name = "Lipid Panel",
            test_status = TestStatus.PENDING,
            ordered_date = datetime.now() - timedelta(days=5),
            patient_id = patient_ident
        )
    ]
    
    db.session.add_all(test_results)
    db.session.commit()