from ..database.models import *
from ..database.connection import db
from sqlalchemy import insert, select
from faker import Faker
from datetime import date, datetime, timedelta
import uuid
import random
import string
from ..extensions import bcrypt
import csv


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

def write_to_csv(dic):
    with open("usernames_passwords.csv", "w", newline='') as csvfile:
        fieldnames = ["username", "password", "role"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dic)
        
def delete_table_data() -> None:
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Data successfully deleted")
    
# Seed the database with the fake data
def seed_database() -> None:
    
    delete_table_data()
    
    print("Seeding database with data...")
    
    doctors = []
    
    # Create 10 doctors
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
    
    # Create 50 patients
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
            email = fake.email(),
            gender = random.choice(list(Gender)),
            height = str(random.uniform(150.0, 200.0)),
            marriage_status = random.choice(list(MaritalStatus)),
            race = random.choice(list(Race))
        )
        patients.append(patient)
    db.session.add_all(patients)
    db.session.commit()
    
    # Patient with id 1 will be assigned the fake data with prescriptions, test_results,
    # and appointments
    
    # The doctors and patients are also to be linked to user accounts for them
    
    login_dic = []
    doctor_logins = []
    for doctor in doctors:
        password = ''.join(random.sample(string.ascii_lowercase, 8))
        new_dic = {"username": f"{doctor.first_name.lower()}.{doctor.last_name.lower()}", 
                   "password": password,
                   "role": "doctor"}
        login_dic.append(new_dic)
        
        password = bytes([ord(char) for char in password])
        
        doctor_login = Doctor_Login(    
            user_name = f"{doctor.first_name.lower()}.{doctor.last_name.lower()}",
            email = doctor.email,
            password = bcrypt.generate_password_hash(password).decode("utf-8"),
            doctor_id = doctor.doctor_id,
            type = "doctor_login"
        )
        
        doctor_logins.append(doctor_login)
    db.session.add_all(doctor_logins)
    db.session.commit()
    
    db.session.execute(insert(doctor_patient_association).values([{"doctor_id": 1, "patient_id": 1}]))
    db.session.commit()
    
    # Now call insert_test_data with patient 1 and doctor 1
    insert_test_data(patients[0].patient_id, 1)  # Use hardcoded doctor ID 1
    
    doctor_ids = db.session.execute(select(Doctor.doctor_id)).scalars().all()
    patient_ids = db.session.execute(select(Patient.patient_id)).scalars().all()
    
    if not doctor_ids or not patient_ids:
        print("No doctors or patients found. Skipping association seeding.")
        exit()
    else:
        associations = []
        for patient_id in patient_ids:
            num_doctors = fake.random_int(min=1, max=3)
            selected_doctors = fake.random_elements(elements=doctor_ids, length=num_doctors, unique=True)
            for doctor_id in selected_doctors:
                associations.append({"doctor_id": doctor_id, "patient_id": patient_id})

        if associations:
            db.session.execute(insert(doctor_patient_association).values(associations))
            db.session.commit()
        
    patient_logins = []
    for patient in patients:
        password = ''.join(random.sample(string.ascii_lowercase, 8))
        new_dic = {"username": f"{patient.first_name.lower()}.{patient.last_name.lower()}", 
                   "password": password,
                   "role": "patient"}
        login_dic.append(new_dic)
        
        password = bytes([ord(char) for char in password])
        
        patient_login = Patient_Login(
            user_name = f"{patient.first_name.lower()}.{patient.last_name.lower()}",
            email = patient.email,
            password = bcrypt.generate_password_hash(password).decode("utf-8"),
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
        password = bcrypt.generate_password_hash("garrett_is_awesome").decode("utf-8"),
        type = "admin_login"
    )
    new_dic = {"username": "admin", 
               "password": "garrett_is_awesome",
               "role": "admin"}
    login_dic.append(new_dic)
    
    db.session.add(admin)
    db.session.commit()
    
    write_to_csv(login_dic)
    
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
    
    # appointments = [
    #     Appointment(
    #         appointment_time = datetime.now() + timedelta(days=14),
    #         clinic_name = "Ohio Medical Center",
    #         state = "Ohio",
    #         city = "Lauration",
    #         patient_id = patient_ident,
    #         doctor_id = doctor_ident
    #     )
    # ]
    # db.session.add_all(appointments)
    # db.session.commit()
    
    test_results = [
        Test_Result(
            test_name = "Complete Blood Couint",
            test_status = TestStatus.COMPLETED,
            ordered_date = datetime.now() - timedelta(days=45),
            result_time = datetime.now() - timedelta(days=42),
            result_value="WBC: 6.5, RBC: 4.2, Hgb: 12.8, Plt: 240",
            unit_of_measure="K/uL, M/uL, g/dL, K/uL",
            reference_range="WBC: 4.5-11.0, RBC: 4.0-5.2, Hgb: 12.0-16.0, Plt: 150-450",
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
    
    db.session.execute(
        insert(Message),
        [
            {"content": "Hello, how are you feeling today?", "sender_type": "doctor", "doctor_id": 1, "patient_id": 1},
            {"content": "I have been feeling better, thank you.", "sender_type": "patient", "doctor_id": 1, "patient_id": 1},
            {"content": "Please remember to take your medication twice a day.", "sender_type": "doctor", "doctor_id": 1, "patient_id": 1},
            {"content": "Got it, I will follow the instructions.", "sender_type": "patient", "doctor_id": 1, "patient_id": 1},
            {"content": "Can we schedule a follow-up appointment next week?", "sender_type": "doctor", "doctor_id": 1, "patient_id": 1},
            {"content": "Are you alive?", "sender_type": "doctor", "doctor_id": 1, "patient_id": 1}
        ]
    )
    
    db.session.execute(
        insert(Billing),
        [
            {"billing_date": "2025-10-05", "billing_amount": 250.00, "notes": "Routine checkup and consultation", "patient_id": 1},
            {"billing_date": "2025-10-04", "billing_amount": 480.00, "notes": "Follow-up visit with lab tests", "patient_id": 2},
            {"billing_date": "2025-10-02", "billing_amount": 1200.00, "notes": "Minor surgical procedure billing", "patient_id": 3}
        ]
    )
    
    db.session.execute(
        insert(Appointment),
        [
            {"appointment_time": "2025-09-21 12:02:30", "clinic_name": "TN Medical Center", "state": "Tennessee", "city": "Nashville", "patient_id": 1, "doctor_id": 1},
            {"appointment_time": "2025-10-07 14:02:30", "clinic_name": "TN Medical Center", "state": "Tennessee", "city": "Nashville", "patient_id": 1, "doctor_id": 1}
        ]
    )
    
    insert_lisa_walters_data()
    
    db.session.commit()
    
def insert_lisa_walters_data():
    patient_id = 2
    doctor_id = 4 
    
    appointments = [
        Appointment(
            appointment_time=datetime(2025, 8, 15, 10, 30, 0),
            clinic_name="City Health Clinic",
            state="California",
            city="Los Angeles",
            patient_id=patient_id,
            doctor_id=doctor_id
        ),
        Appointment(
            appointment_time=datetime.now() + timedelta(days=25),
            clinic_name="City Health Clinic",
            state="California",
            city="Los Angeles",
            patient_id=patient_id,
            doctor_id=doctor_id
        )
    ]
    db.session.add_all(appointments)

    prescriptions = [
        Prescription(
            medication_name="Amoxicillin",
            dosage="500mg",
            frequency_taken="Every 8 hours for 7 days",
            notes="Finish all medication even if feeling better.",
            patient_id=patient_id,
            doctor_id=doctor_id
        ),
        Prescription(
            medication_name="Ibuprofen",
            dosage="400mg",
            frequency_taken="As needed for pain, max 3 times a day",
            notes="Take with food to avoid stomach upset.",
            patient_id=patient_id,
            doctor_id=doctor_id
        )
    ]
    db.session.add_all(prescriptions)

    test_results = [
        Test_Result(
            test_name="Thyroid Stimulating Hormone (TSH)",
            test_status=TestStatus.COMPLETED,
            ordered_date=datetime(2025, 8, 15),
            result_time=datetime(2025, 8, 17),
            result_value="2.1",
            unit_of_measure="mIU/L",
            reference_range="0.4 - 4.0",
            result_notes="TSH level is within the normal range.",
            patient_id=patient_id
        ),
        Test_Result(
            test_name="Vitamin D, 25-Hydroxy",
            test_status=TestStatus.PENDING,
            ordered_date=datetime.now() - timedelta(days=2),
            patient_id=patient_id
        ),
        Test_Result(
            test_name="Thyroid Stimulating Hormone (TSH)",
            test_status=TestStatus.ABNORMAL,
            ordered_date=datetime(2025, 8, 15),
            result_time=datetime(2025, 8, 17),
            result_value="2.1",
            unit_of_measure="mIU/L",
            reference_range="0.4 - 4.0",
            result_notes="TSH level is within the normal range.",
            patient_id=patient_id
        ),
        
    ]
    db.session.add_all(test_results)

    billings = [
        Billing(
            billing_amount=150.00,
            billing_date=datetime(2025, 8, 15),
            notes="Consultation Fee",
            patient_id=patient_id
        ),
        Billing(
            billing_amount=75.50,
            billing_date=datetime(2025, 8, 17),
            notes="Lab Work: TSH Test",
            patient_id=patient_id
        )
    ]
    db.session.add_all(billings)
    
    # --- Insurance Information ---
    insurance = Insurance(
        member_id="WALTERS98765",
        primary_insurance="Blue Cross Blue Shield",
        group_number="BCBS-GRP-555",
        plan_type="PPO",
        patient_id=patient_id
    )
    db.session.add(insurance)
    db.session.commit()