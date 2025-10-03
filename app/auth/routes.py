from flask import Blueprint, render_template, url_for,  request, redirect, flash
from flask_login import logout_user, login_required, login_user, current_user
from ..extensions import bcrypt
from ..database.models import *
from ..database.connection import db
from datetime import datetime
import uuid
import random

auth_bp = Blueprint("auth", __name__, template_folder="templates")

def calculate_age(dob) -> str:
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

# Register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    
    
    if request.method == 'POST':
        # Handle registration form (save to DB later if needed)
        first_name = request.form.get("First-Name")
        last_name = request.form.get("Last-Name")
        email = request.form.get("Email")
        username = request.form.get("Username")
        password = request.form.get("Password")
        phone_number = request.form.get("Phone-Number")
        address = request.form.get("Address")
        zip_code = request.form.get("Zip-code")
        city = request.form.get("City")
        dob_str = request.form.get("DateOfBirth")
        sex = request.form.get("Sex")
        role = request.form.get("role", "patient")
        
        if User_Login.query.filter_by(user_name=username).first():
            flash("Username already exists. Please choose another username.", "danger")
            return redirect(url_for('auth.register'))
        
        if User_Login.query.filter_by(email=email).first():
            flash("Email already exists. Please choose another email.", "danger")
            return redirect(url_for('auth.register'))
        
        try:
            dob_object = datetime.strptime(dob_str, "%m/%d/%Y")
            dob = dob_object.date()
            
            age = calculate_age(dob)
            
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        
            patient_code = str(uuid.uuid4())
            
            gender_map = {
                "Male": Gender.MALE,
                "Female": Gender.FEMALE,
                "Other": Gender.OTHER
            }
            gender = gender_map.get(sex, Gender.OTHER)
            
            full_address = f"{address}, {city}, {zip_code}"
            
            new_patient = Patient(
                patient_code = patient_code,
                first_name = first_name,
                last_name = last_name,
                dob= dob,
                age= age,
                address = full_address,
                phone_number = phone_number,
                email = email,
                gender = gender,
                height = 0.0,  # Default height, can be updated later
                doctor_id = random.randint(1, 10)  # Assign to default doctor (ID 1), update this logic as needed
            )
        
            db.session.add(new_patient)
            db.session.flush()
            
            new_user = Patient_Login(
                user_name = username,
                email = email,
                password = hashed_password,
                patient_id = new_patient.patient_id
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            
            flash(f'Registration successful!')
            return redirect(url_for('patient.patient_home'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error occured during registrationL {str(e)}")
            return redirect(url_for('auth.register'))
            
    return render_template('register.html', title="Register")

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('patient.patient_home'))
    
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
        
        # Find user based on role
        user = None
        if role == "patient":
            user = Patient_Login.query.filter_by(user_name=username).first()
        elif role == "doctor":
            user = Doctor_Login.query.filter_by(user_name=username).first()
        elif role == "admin":
            user = Admin_Login.query.filter_by(user_name=username).first()
        else:
            flash("Invalid role selected", "danger")
            return redirect(url_for('auth.login'))
        
        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {username}!", "success")
            
            # Redirect based on role
            if role == "patient":
                return redirect(url_for('patient.patient_home'))
            elif role == "doctor":
                return redirect(url_for('doctor.dashboard'))  # You'll need to create this
            else:
                return redirect(url_for('admin.dashboard'))  # You'll need to create this
        else:
            flash("Invalid username or password!", "danger")
            return redirect(url_for('auth.login', role=role))

    return render_template("login.html", role=role, title="Login")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))