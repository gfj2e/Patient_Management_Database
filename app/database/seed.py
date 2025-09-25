from ..database.models import *
from ..database.connection import db
from faker import Faker
import random
import uuid

fake = Faker()

SPECIALTIES = ("Family Medicine", "Cardiology", "Pediatrics", "Neurology",
               "Orthopedics", "Dermatology", "Gynecology", "Oncology")

def generate_phone_number():
    number = "("
    
    area_code = random.randint(200, 999)
    number += str(area_code) + ") "
    
    sub1 = ''.join(str(random.randint(0, 9)) for i in range(3))
    
    number += sub1 + "-"
    
    sub2 = ''.join(str(random.randint(0, 9)) for i in range(4))
    number += sub2
    
    return number

def seed_database():
    if Doctor.query.count() > 0:
        print("Database already exists")
        return False
    
    print("Seeding database with data...")
    
    doctors = []
    
    for i in range(10):
        doctor = Doctor(
            first_name = fake.first_name(),
            last_name = fake.last_name(),
            specialty = random.choice(SPECIALTIES),
            state = fake.state(),
            city = fake.city(),
            phone_number = generate_phone_number(),
            email = fake.email(),
            is_accepting_new_patients = random.choice([True, False])
        )
        doctors.append(doctor)
    db.session.add_all(doctors)
    db.session.commit()
    
    patients = []
    
    for i in range(50):
        patient = Patient(
            patient_code = str(uuid.uuid4())[:16],
            first_name = fake.first_name(),
            last_name = fake.last_name(),
            dob = fake.date_of_birth(),
            address = fake.address().replace('\n', ', '),
            phone_number = generate_phone_number(),
            email = fake.email(),
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
    
    admin = Admin_Login(
        user_name = "admin",
        email = "admin@garrettisgreat.com",
        password = "garrett_is_awesome",
        type = "admin_login"
    )
    
    print("Database seeding complete!")
    return True