from flask import Blueprint, render_template, url_for,  request, redirect, flash
from flask_login import logout_user, login_required, login_user, current_user
from sqlalchemy import select
from ..extensions import bcrypt
from ..database.models import *
from ..database.connection import db
from datetime import datetime, date
from decimal import Decimal
import uuid
import traceback
import random

auth_bp = Blueprint("auth", __name__, template_folder="templates")

def calculate_age(dob) -> int:
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

# Register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('patient.patient_home'))

    if request.method == 'POST':
        first_name = request.form.get("First-Name")
        last_name = request.form.get("Last-Name")
        email = request.form.get("Email")
        username = request.form.get("Username")
        password = request.form.get("Password")
        phone = request.form.get("Phone-Number")
        address = request.form.get("Address")
        zip_code = request.form.get("Zip-code")
        city = request.form.get("City")
        dob_str = request.form.get("DateOfBirth")
        sex = request.form.get("Sex")

        if not all([first_name, last_name, email, username, password, phone, address, zip_code, city, dob_str, sex]):
            flash("All fields are required.", "danger")
            return redirect(url_for('auth.register'))

        #if User_Login.query.filter_by(user_name=username).first():
        if db.session.execute(select(User_Login).where(User_Login.user_name == username)).scalar():
            flash("Username already exists. Please choose another username.", "danger")
            return redirect(url_for('auth.register'))
        # if User_Login.query.filter_by(email=email).first():
        if db.session.execute(select(User_Login).where(User_Login.email == email)).scalar():
            flash("Email already exists. Please choose another email.", "danger")
            return redirect(url_for('auth.register'))

        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            age = calculate_age(dob)

            gender = {
                "Male": Gender.MALE,
                "Female": Gender.FEMALE,
                "Other": Gender.OTHER
            }.get(sex, Gender.OTHER)

            full_address = f"{address}, {city}, {zip_code}"
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

            new_patient = Patient(
                patient_code = str(uuid.uuid4()),
                first_name = first_name,
                last_name = last_name,
                dob = dob,
                age = age,
                address = full_address,
                phone_number = phone,
                email = email,
                gender = gender,
                height = Decimal('0.00'),
                doctor_id = random.randint(1, 10)
            )
            db.session.add(new_patient)
            db.session.flush()

            new_user = Patient_Login(
                user_name=username,
                email=email,
                password=hashed_password,
                patient_id=new_patient.patient_id,
                type="patient_login"
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash("Registration successful! Welcome to CuraCloud.", "success")
            return redirect(url_for('patient.patient_home'))

        except Exception as e:
            db.session.rollback()
            return redirect(url_for('auth.register'))

    return render_template('register.html', title="Register")

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Patient_Login):
            return redirect(url_for('patient.patient_home'))
        elif isinstance(current_user, Doctor_Login):
            return redirect(url_for('doctor.doctor_home'))
        else:
            return redirect(url_for('main.index'))
    
    role = request.args.get("role")
    if not role:
        role = "patient"

    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return redirect(url_for('auth.login', role=role))
        
        user = None
        if role == "patient":
            user = db.session.execute(select(Patient_Login).where(Patient_Login.user_name == username)).scalar()
        elif role == "doctor":
            user = db.session.execute(select(Doctor_Login).where(Doctor_Login.user_name == username)).scalar()
        elif role == "admin":
            user = db.session.execute(select(Admin_Login).where(Admin_Login.user_name == username)).scalar()
        else:
            flash("Invalid role selected", "danger")
            return redirect(url_for('auth.login'))
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {username}!", "success")
            
            if role == "patient":
                return redirect(url_for('patient.patient_home'))
            elif role == "doctor":
                return redirect(url_for('doctor.doctor_home'))
            else:
                return redirect(url_for('admin.admin_home'))
        else:
            flash("Invalid username or password!", "danger")
            return redirect(url_for('auth.login', role=role))

    return render_template("login.html", role=role, title="Login")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for("main.index"))