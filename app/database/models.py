from .connection import db
from sqlalchemy import TIMESTAMP, func, String, Text, ForeignKey, Boolean, Date, Enum as SQLEnum, DECIMAL, DateTime, SmallInteger
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

# Defining the tables using SQLAlchemy
# Tables:
#     doctors
#     patients
#     appointments
#     test_results
#     prescriptions
#     patient_login
#     doctor_login
#     admin_login

# Enums for defining various choices for tables
class Gender(PyEnum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class MaritalStatus(PyEnum):
    SINGLE = "Single"
    MARRIED = "Married"
    OTHER = "Other"

class Race(PyEnum):
    WHITE = "White"
    BLACK = "Black"
    NATIVE_AMERICAN = "Native American"
    ASIAN = "Asian"
    HAWAIIAN_PACIFIC = "Native Hawaiian/Pacific Islander"
    OTHER_MIXED = "Other/Mixed"
    
class TestStatus(PyEnum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# Defining the tables
# General format of defining a column is
#! column_name: Mapped[python var] = mapped_column(SQLAlchemy var, different properties)
# For example:
# first_name: Mapped[str] = mapped_column(String(50), nullable=False)

class Doctor(db.Model):
    __tablename__ = "doctors"

    doctor_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    specialty: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    patients = relationship("Patient", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
    login = relationship("Doctor_Login", back_populates="doctor", uselist=False)
    
    is_accepting_new_patients: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
class Patient(db.Model):
    __tablename__ = "patients"
    
    patient_id: Mapped[int] = mapped_column(primary_key=True)
    patient_code: Mapped[str] = mapped_column(String(36), nullable=False)
    
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    
    address: Mapped[str] = mapped_column(Text, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(25))
    email: Mapped[str] = mapped_column(String(255))
    
    gender: Mapped[Gender] = mapped_column(SQLEnum(Gender), nullable=False)
    height: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)
    marriage_status: Mapped[MaritalStatus] = mapped_column(SQLEnum(MaritalStatus))
    race: Mapped[Race] = mapped_column(SQLEnum(Race))
    
    insurance_id: Mapped[str] = mapped_column(String(255))
    
    doctor = relationship("Doctor", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    test_results = relationship("Test_Result", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    login = relationship("Patient_Login", back_populates="patient", uselist=False)
    
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"))
    
class Appointment(db.Model):
    __tablename__ = "appointments"
    
    appointment_id: Mapped[int] = mapped_column(primary_key=True)
    appointment_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    clinic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"))
    
class Test_Result(db.Model):
    __tablename__ = "test_results"
    
    test_id: Mapped[int] = mapped_column(primary_key=True)
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_status: Mapped[TestStatus] = mapped_column(SQLEnum(TestStatus), default=TestStatus.PENDING, nullable=False)
    ordered_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    result_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    result_value: Mapped[str] = mapped_column(String(255), nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(255), nullable=True)
    reference_range: Mapped[str] = mapped_column(String(255), nullable=True)
    is_abnormal: Mapped[bool] = mapped_column(Boolean, default=False)
    
    result_notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    patient = relationship("Patient", back_populates="test_results")
    
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)

class Prescription(db.Model):
    __tablename__ = "prescriptions"
    
    prescription_id: Mapped[int] = mapped_column(primary_key=True)
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    dosage: Mapped[str] = mapped_column(String(50), nullable=False)
    frequency_taken: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(Text)
    
    doctor = relationship("Doctor", back_populates="prescriptions")
    patient = relationship("Patient", back_populates="prescriptions")
    
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"), nullable=False)

# Using polymorphic inheritance to inherit columns from user logins,
# which patient_login, doctor_login, and admin_login inherit from
# Columns inherited are user_name, email, password, and date_created
#! For more info, see https://docs.sqlalchemy.org/en/20/orm/inheritance.html
class User_Login(db.Model):
    __tablename__ = "user_login"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    date_created: Mapped[datetime] = mapped_column(server_default=func.UTC_TIMESTAMP())
    type: Mapped[str] = mapped_column(String(20))
    
    __mapper_args__ = {
        "polymorphic_identity": "user_login",
        "polymorphic_on": "type"
    }

class Patient_Login(User_Login):
    __tablename__ = "patient_login"
    
    id: Mapped[int] = mapped_column(ForeignKey("user_login.id"), primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    
    login = relationship("Patient", back_populates="login", uselist=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "patient_login"
    }
    
class Doctor_Login(User_Login):
    __tablename__ = "doctor_login"
    
    id: Mapped[int] = mapped_column(ForeignKey("user_login.id"), primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"))
    
    login = relationship("Doctor", back_populates="login", uselist=False)

    __mapper_args__ = {
        "polymorphic_identity": "doctor_login"
    }
    
class Admin_Login(User_Login):
    __tablename__ = "admin_login"
    
    id: Mapped[int] = mapped_column(ForeignKey("user_login.id"), primary_key=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "admin_login"
    }