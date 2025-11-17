from flask import Blueprint, render_template, url_for,  request, redirect, flash
from flask_login import logout_user, login_required, login_user, current_user
from sqlalchemy import select
from ..extensions import bcrypt
from ..database.models import *
from ..database.connection import db
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from .mailer import send_reset_email
import uuid
import random
import secrets
from utils.logger import log_event


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

    doctors = db.session.execute(select(Doctor)).scalars().all()

    if request.method == 'POST':

        first_name = request.form.get("First_Name")
        last_name = request.form.get("Last_Name")
        email = request.form.get("Email")
        username = request.form.get("Username")
        password = request.form.get("Password")
        phone = request.form.get("Phone-Number")
        address = request.form.get("Address")
        zip_code = request.form.get("Zip-code")
        city = request.form.get("City")
        dob_str = request.form.get("DateOfBirth")
        sex = request.form.get("Sex")
        doctor_id = request.form.get("DoctorID")

        # if not all([first_name, last_name, email, username, password, phone,
        #             address, zip_code, city, dob_str, sex, doctor_id]):
        #     flash("All fields are required.", "danger")
        #     return redirect(url_for('auth.register'))

        required_fields = [first_name, last_name, email, username, password, phone,
                   address, zip_code, city, dob_str, sex]

        if not all(required_fields):
            flash("All fields are required.", "danger")
            return redirect(url_for('auth.register'))

        if not doctor_id or doctor_id == "":
            flash("Please select a doctor.", "danger")
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
                patient_code=str(uuid.uuid4()),
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                age=age,
                address=full_address,
                phone_number=phone,
                email=email,
                gender=gender,
                height=Decimal('0.00'),
                # doctor_id=int(doctor_id) 
            )

            db.session.add(new_patient)
            db.session.flush()

            selected_doctor = db.session.get(Doctor, int(doctor_id))
            new_patient.doctors.append(selected_doctor)

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
            print("REGISTRATION ERROR:", e)
            flash("Registration failed.", "danger")
            return redirect(url_for('auth.register'))

    return render_template('register.html', doctors=doctors, title="Register")


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

            log_event(
                "login",
                f"{role.capitalize()} '{username}' logged in",
                target_type="user",
                target_id=user.id
            )

            # flash(f"Welcome back, {username}!", "success")
            
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

@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        if isinstance(current_user, Patient_Login):
            return redirect(url_for('patient.patient_home'))
        elif isinstance(current_user, Doctor_Login):
            return redirect(url_for('doctor.doctor_home'))
        else:
            return redirect(url_for('main.index'))
    

    if request.method == "POST":
        username = request.form.get("username")
        
        user = db.session.execute(select(Patient_Login).where(Patient_Login.user_name == username)).scalar()
        
        if not user:
            flash("No patient found with that username.", "error")
            return redirect(url_for('auth.reset_password', role='patient'))
        
        token = secrets.token_urlsafe(36)
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        
        reset_link = url_for('auth.reset_with_token', token=token, _external=True) 
        
        try:
            email_sent = send_reset_email(user.patient.email, reset_link)
            if email_sent:
                flash("Password email sent", "success")
                print(f"Reset email sent to {user.email}")
            else:
                flash("Failed to send reset email. Try again later", "error")
                print(f"Failed to send reset to {user.email}")
        except Exception as e:
            flash("Error sending email.", "error")
            print(f"Exception in sending an email: {e}")
        
        return redirect(url_for('auth.login', role='patient'))

    
    return render_template('reset_password.html')

@auth_bp.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    if current_user.is_authenticated:
        if isinstance(current_user, Patient_Login):
            return redirect(url_for('patient.patient_home'))
        # elif isinstance(current_user, Doctor_Login):
        #     return redirect(url_for('doctor.doctor_home'))
        # else:
        #     return redirect(url_for('main.index'))
        else:
            flash("Only patients can reset their password.", "error")
            return redirect(url_for('auth.login'))
        
    # role = request.args.get("role")
    # if role != "patient":
    #     flash("Must be a patient to reset password", "error")
    #     return redirect(url_for('auth.login'))

    user = db.session.execute(select(Patient_Login).where(Patient_Login.reset_token == token)).scalar()
    if not user:
        flash("Invalid or expired token", "error")
        return redirect(url_for('auth.reset_password'))
    
    current_time = datetime.now(timezone.utc)
    if user.reset_token_expires is None or user.reset_token_expires.replace(tzinfo=timezone.utc) < current_time:
        flash("This reset link has expired. Please request a new one.", "error")
        
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        return redirect(url_for('auth.reset_password', role='patient'))
    
    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not new_password:
            flash("Password is required", "error")
            return render_template('reset_with_token.html', token=token)
            
        if len(new_password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template('reset_with_token.html', token=token)
            
        # confirm password validation
        if confirm_password and new_password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('reset_with_token.html', token=token)
        
        user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        return redirect(url_for('auth.login', role='patient'))
    
    return render_template('reset_with_token.html')

@auth_bp.route('/logout')
@login_required
def logout():

    log_event(
    "logout",
    f"User '{current_user.user_name}' logged out",
    target_type="user",
    target_id=current_user.id
)
        
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.index"))