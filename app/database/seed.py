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
            test_name = "Complete Blood Count",
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
    
    insert_comprehensive_patient_data()
    
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
    
from ..database.models import *
from ..database.connection import db
from datetime import datetime, timedelta
from sqlalchemy import select

def insert_comprehensive_patient_data():
    """
    Fills the first three patients with comprehensive sample data including:
    - Appointments (past, upcoming)
    - Test Results (completed, pending, abnormal)
    - Prescriptions
    - Billing records
    - Insurance information
    - Messages with doctors
    - Prescription refill requests
    """
    
    # ===== PATIENT 1: Comprehensive Data =====
    patient_1_id = 1
    doctor_1_id = 1
    
    # More appointments for patient 1
    appointments_p1 = [
        Appointment(
            appointment_time=datetime(2024, 12, 10, 9, 0, 0),
            clinic_name="TN Medical Center",
            state="Tennessee",
            city="Nashville",
            patient_id=patient_1_id,
            doctor_id=doctor_1_id
        ),
        Appointment(
            appointment_time=datetime.now() + timedelta(days=30),
            clinic_name="TN Medical Center",
            state="Tennessee",
            city="Nashville",
            patient_id=patient_1_id,
            doctor_id=doctor_1_id
        )
    ]
    db.session.add_all(appointments_p1)
    
    # Additional test results for patient 1
    test_results_p1 = [
        Test_Result(
            test_name="HbA1c (Diabetes Monitoring)",
            test_status=TestStatus.COMPLETED,
            ordered_date=datetime.now() - timedelta(days=90),
            result_time=datetime.now() - timedelta(days=87),
            result_value="6.8",
            unit_of_measure="%",
            reference_range="<5.7%",
            result_notes="Slightly elevated. Continue medication and diet modifications.",
            patient_id=patient_1_id
        ),
        Test_Result(
            test_name="Basic Metabolic Panel",
            test_status=TestStatus.COMPLETED,
            ordered_date=datetime.now() - timedelta(days=30),
            result_time=datetime.now() - timedelta(days=28),
            result_value="Na: 140, K: 4.2, Cl: 102, CO2: 25, BUN: 18, Creat: 0.9, Glucose: 105",
            unit_of_measure="mEq/L, mEq/L, mEq/L, mEq/L, mg/dL, mg/dL, mg/dL",
            reference_range="Na: 136-145, K: 3.5-5.0, Cl: 98-107, CO2: 23-29, BUN: 7-20, Creat: 0.6-1.2, Glucose: 70-100",
            result_notes="All values within normal range except glucose slightly elevated.",
            patient_id=patient_1_id
        ),
        Test_Result(
            test_name="Urinalysis",
            test_status=TestStatus.PENDING,
            ordered_date=datetime.now() - timedelta(days=3),
            patient_id=patient_1_id
        )
    ]
    db.session.add_all(test_results_p1)
    
    # Insurance for patient 1
    insurance_p1 = Insurance(
        member_id="P001-MEMBER",
        primary_insurance="Aetna",
        group_number="AETNA-GRP-12345",
        plan_type="HMO",
        patient_id=patient_1_id
    )
    db.session.add(insurance_p1)
    
    # Additional billing for patient 1
    billing_p1 = [
        Billing(
            billing_amount=325.00,
            billing_date=datetime.now() - timedelta(days=90),
            notes="Quarterly diabetes management consultation",
            patient_id=patient_1_id
        ),
        Billing(
            billing_amount=125.00,
            billing_date=datetime.now() + timedelta(days=5),
            notes="Lab work - HbA1c and metabolic panel",
            patient_id=patient_1_id
        )
    ]
    db.session.add_all(billing_p1)
    
    # Get the actual prescription IDs for patient 1 (created in insert_test_data)
    # Prescriptions 1, 2, 3 should exist for patient 1
    db.session.commit()  # Ensure prescriptions are committed and have IDs
    
    # Prescription refill requests for patient 1
    refill_requests_p1 = [
        PrescriptionRefillRequest(
            request_date=datetime.now() - timedelta(days=5),
            status=RefillStatus.APPROVED,
            notes="Approved for 90-day supply",
            patient_id=patient_1_id,
            doctor_id=doctor_1_id,
            prescription_id=1  # Lisinopril (created in insert_test_data)
        ),
        PrescriptionRefillRequest(
            request_date=datetime.now() - timedelta(days=1),
            status=RefillStatus.PENDING,
            notes="Requested refill online",
            patient_id=patient_1_id,
            doctor_id=doctor_1_id,
            prescription_id=3  # Metformin (created in insert_test_data)
        )
    ]
    db.session.add_all(refill_requests_p1)
    
    # ===== PATIENT 2: Comprehensive Data =====
    patient_2_id = 2
    doctor_2_id = 4
    
    # Additional appointments for patient 2
    appointments_p2 = [
        Appointment(
            appointment_time=datetime(2025, 7, 20, 14, 0, 0),
            clinic_name="City Health Clinic",
            state="California",
            city="Los Angeles",
            patient_id=patient_2_id,
            doctor_id=doctor_2_id
        ),
        Appointment(
            appointment_time=datetime.now() + timedelta(days=45),
            clinic_name="City Health Clinic",
            state="California",
            city="Los Angeles",
            patient_id=patient_2_id,
            doctor_id=doctor_2_id
        )
    ]
    db.session.add_all(appointments_p2)
    
    # More test results for patient 2
    test_results_p2 = [
        Test_Result(
            test_name="Complete Blood Count (CBC)",
            test_status=TestStatus.COMPLETED,
            ordered_date=datetime(2025, 8, 15),
            result_time=datetime(2025, 8, 16),
            result_value="WBC: 7.2, RBC: 4.5, Hgb: 13.5, Plt: 220",
            unit_of_measure="K/uL, M/uL, g/dL, K/uL",
            reference_range="WBC: 4.5-11.0, RBC: 4.0-5.2, Hgb: 12.0-16.0, Plt: 150-450",
            result_notes="All values within normal limits",
            patient_id=patient_2_id
        ),
        Test_Result(
            test_name="Chest X-Ray",
            test_status=TestStatus.COMPLETED,
            ordered_date=datetime.now() - timedelta(days=60),
            result_time=datetime.now() - timedelta(days=60),
            result_value="Clear",
            unit_of_measure="N/A",
            reference_range="N/A",
            result_notes="No acute cardiopulmonary abnormalities detected.",
            patient_id=patient_2_id
        )
    ]
    db.session.add_all(test_results_p2)
    
    # Additional billing for patient 2
    billing_p2 = [
        Billing(
            billing_amount=95.00,
            billing_date=datetime.now() - timedelta(days=60),
            notes="X-ray imaging service",
            patient_id=patient_2_id
        ),
        Billing(
            billing_amount=200.00,
            billing_date=datetime.now() + timedelta(days=10),
            notes="Follow-up consultation and medication review",
            patient_id=patient_2_id
        )
    ]
    db.session.add_all(billing_p2)
    
    # Messages for patient 2
    messages_p2 = [
        Message(
            content="Hi Lisa, please remember to take your Amoxicillin for the full 7 days.",
            sender_type="doctor",
            patient_id=patient_2_id,
            doctor_id=doctor_2_id
        ),
        Message(
            content="Thank you, Dr. I've been taking it as prescribed.",
            sender_type="patient",
            patient_id=patient_2_id,
            doctor_id=doctor_2_id
        ),
        Message(
            content="Great! Let me know if you experience any side effects.",
            sender_type="doctor",
            patient_id=patient_2_id,
            doctor_id=doctor_2_id
        )
    ]
    db.session.add_all(messages_p2)
    
    # Commit to get prescription IDs for patient 2
    db.session.commit()
    
    # Get the prescription IDs we just created for patient 2
    patient_2_prescriptions = db.session.execute(
        select(Prescription).where(Prescription.patient_id == patient_2_id)
    ).scalars().all()
    
    # Prescription refill requests for patient 2 (use actual prescription ID)
    if len(patient_2_prescriptions) > 0:
        refill_requests_p2 = [
            PrescriptionRefillRequest(
                request_date=datetime.now() - timedelta(days=10),
                status=RefillStatus.APPROVED,
                notes="Refill approved",
                patient_id=patient_2_id,
                doctor_id=doctor_2_id,
                prescription_id=patient_2_prescriptions[0].prescription_id  # First prescription (Amoxicillin from insert_test_data)
            )
        ]
        db.session.add_all(refill_requests_p2)
    
    # ===== PATIENT 3: Comprehensive Data =====
    patient_3_id = 3
    doctor_3_id = 2
    
    # Appointments for patient 3
    appointments_p3 = [
        Appointment(
            appointment_time=datetime(2025, 6, 5, 11, 30, 0),
            clinic_name="Metro Health Associates",
            state="New York",
            city="New York",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Appointment(
            appointment_time=datetime(2025, 9, 10, 10, 0, 0),
            clinic_name="Metro Health Associates",
            state="New York",
            city="New York",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Appointment(
            appointment_time=datetime.now() + timedelta(days=20),
            clinic_name="Metro Health Associates",
            state="New York",
            city="New York",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        )
    ]
    db.session.add_all(appointments_p3)
    
    # Prescriptions for patient 3
    prescriptions_p3 = [
        Prescription(
            medication_name="Levothyroxine",
            dosage="75mcg",
            frequency_taken="Once daily on empty stomach",
            notes="For hypothyroidism. Take 30-60 minutes before breakfast.",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Prescription(
            medication_name="Omeprazole",
            dosage="20mg",
            frequency_taken="Once daily before breakfast",
            notes="For acid reflux. Can take with or without food.",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Prescription(
            medication_name="Vitamin D3",
            dosage="2000 IU",
            frequency_taken="Once daily with food",
            notes="Supplement for vitamin D deficiency.",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Prescription(
            medication_name="test",
            dosage="75mcg",
            frequency_taken="Once daily on empty stomach",
            notes="For hypothyroidism. Take 30-60 minutes before breakfast.",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
    ]
    db.session.add_all(prescriptions_p3)
    
    # Test results for patient 3
    test_results_p3 = [
        Test_Result(
            test_name="Thyroid Panel (TSH, T3, T4)",
            test_status=TestStatus.COMPLETED,
            ordered_date=datetime.now() - timedelta(days=120),
            result_time=datetime.now() - timedelta(days=118),
            result_value="TSH: 3.2, T3: 95, T4: 7.8",
            unit_of_measure="mIU/L, ng/dL, mcg/dL",
            reference_range="TSH: 0.4-4.0, T3: 80-200, T4: 5.0-12.0",
            result_notes="Thyroid function within normal range on current medication.",
            patient_id=patient_3_id
        ),
        Test_Result(
            test_name="Lipid Panel",
            test_status=TestStatus.ABNORMAL,
            ordered_date=datetime.now() - timedelta(days=45),
            result_time=datetime.now() - timedelta(days=43),
            result_value="Total Chol: 245, LDL: 160, HDL: 42, Triglycerides: 215",
            unit_of_measure="mg/dL, mg/dL, mg/dL, mg/dL",
            reference_range="Total <200, LDL <100, HDL >40, Trig <150",
            result_notes="Elevated cholesterol and triglycerides. Recommend dietary changes and consider statin therapy.",
            patient_id=patient_3_id
        ),
        Test_Result(
            test_name="Vitamin D, 25-Hydroxy",
            test_status=TestStatus.COMPLETED,
            ordered_date=datetime.now() - timedelta(days=90),
            result_time=datetime.now() - timedelta(days=88),
            result_value="22",
            unit_of_measure="ng/mL",
            reference_range="30-100",
            result_notes="Vitamin D deficiency. Started on supplementation.",
            patient_id=patient_3_id
        ),
        Test_Result(
            test_name="Comprehensive Metabolic Panel",
            test_status=TestStatus.PENDING,
            ordered_date=datetime.now() - timedelta(days=2),
            patient_id=patient_3_id
        )
    ]
    db.session.add_all(test_results_p3)
    
    # Billing for patient 3
    billing_p3 = [
        Billing(
            billing_amount=450.00,
            billing_date=datetime(2025, 6, 5),
            notes="Annual physical examination with lab work",
            patient_id=patient_3_id
        ),
        Billing(
            billing_amount=180.00,
            billing_date=datetime(2025, 9, 10),
            notes="Follow-up visit for thyroid management",
            patient_id=patient_3_id
        ),
        Billing(
            billing_amount=95.00,
            billing_date=datetime.now() + timedelta(days=15),
            notes="Lab work - Comprehensive metabolic panel",
            patient_id=patient_3_id
        )
    ]
    db.session.add_all(billing_p3)
    
    # Insurance for patient 3
    insurance_p3 = Insurance(
        member_id="P003-NYH-789",
        primary_insurance="UnitedHealthcare",
        group_number="UHC-GRP-98765",
        plan_type="PPO",
        patient_id=patient_3_id
    )
    db.session.add(insurance_p3)
    
    # Messages for patient 3
    messages_p3 = [
        Message(
            content="Hello! Your recent lab results show elevated cholesterol. I'd like to discuss treatment options.",
            sender_type="doctor",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Message(
            content="Thank you for letting me know. Should I schedule an appointment?",
            sender_type="patient",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Message(
            content="Yes, please. Let's meet within the next 2-3 weeks to review your lipid panel and discuss lifestyle modifications.",
            sender_type="doctor",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Message(
            content="I've scheduled an appointment for next week. Looking forward to it.",
            sender_type="patient",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        ),
        Message(
            content="Perfect! Also, please continue taking your Levothyroxine as prescribed.",
            sender_type="doctor",
            patient_id=patient_3_id,
            doctor_id=doctor_3_id
        )
    ]
    db.session.add_all(messages_p3)
    
    # Commit to get prescription IDs for patient 3
    db.session.commit()
    
    # Get the prescription IDs we just created for patient 3
    patient_3_prescriptions = db.session.execute(
        select(Prescription).where(Prescription.patient_id == patient_3_id)
    ).scalars().all()
    
    # Prescription refill requests for patient 3 (use actual prescription IDs)
    if len(patient_3_prescriptions) >= 3:
        refill_requests_p3 = [
            PrescriptionRefillRequest(
                request_date=datetime.now() - timedelta(days=30),
                status=RefillStatus.APPROVED,
                notes="Approved 90-day supply",
                patient_id=patient_3_id,
                doctor_id=doctor_3_id,
                prescription_id=patient_3_prescriptions[0].prescription_id  # Levothyroxine
            ),
            PrescriptionRefillRequest(
                request_date=datetime.now() - timedelta(days=2),
                status=RefillStatus.PENDING,
                notes="Requested refill for Omeprazole",
                patient_id=patient_3_id,
                doctor_id=doctor_3_id,
                prescription_id=patient_3_prescriptions[1].prescription_id  # Omeprazole
            ),
            PrescriptionRefillRequest(
                request_date=datetime.now() - timedelta(days=15),
                status=RefillStatus.DENIED,
                notes="Denied - patient needs follow-up appointment first to review lipid panel results before continuing medications.",
                patient_id=patient_3_id,
                doctor_id=doctor_3_id,
                prescription_id=patient_3_prescriptions[2].prescription_id  # Vitamin D3
            )
        ]
        db.session.add_all(refill_requests_p3)
    
    db.session.commit()
    print("Comprehensive patient data added for patients 1, 2, and 3!")
