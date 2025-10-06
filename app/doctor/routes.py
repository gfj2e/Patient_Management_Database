from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from ..database.models import Doctor_Login, Appointment, Patient, Message
from datetime import datetime, date


auth_bp = Blueprint("auth", __name__, template_folder="templates") 
doctor_bp = Blueprint("doctor", __name__, template_folder="templates")

@doctor_bp.route("/doctor")
@login_required
def doctor_home():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        doctor_name = f"{doctor.first_name} {doctor.last_name}"

        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time >= datetime.now()
        ).order_by(Appointment.appointment_time).all()

        patients = Patient.query.filter_by(doctor_id=doctor.doctor_id).all()


        messages_count = len(doctor.messages)


        return render_template("doctor_home.html", 
                               doctor=doctor, 
                               doctor_name=doctor_name, 
                               appointments=upcoming_appointments,
                               patients=list(patients),
                               messages_count=messages_count
                               )
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))



@doctor_bp.route("/doctor/appointments")
@login_required
def doctor_appointments():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        now = datetime.now()


        # Today's appointments
        todays_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time.between(
                datetime.combine(date.today(), datetime.min.time()),
                datetime.combine(date.today(), datetime.max.time())
            )
        ).order_by(Appointment.appointment_time).all()

        # Upcoming appointments (after today)
        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time > datetime.combine(date.today(), datetime.max.time())
        ).order_by(Appointment.appointment_time).all()

        # Past appointments (before today)
        past_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time < datetime.combine(date.today(), datetime.min.time())
        ).order_by(Appointment.appointment_time.desc()).all()

        return render_template(
            "doctor_appointments.html",
            doctor=doctor,
            todays_appointments=todays_appointments,
            upcoming_appointments=upcoming_appointments,
            past_appointments=past_appointments
        )
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))
    
@doctor_bp.route("/doctor/messages")
@login_required
def doctor_messages():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor

        # Query all messages for this doctor
        messages = doctor.messages  # already a list of Message objects

        return render_template(
            "doctor_messages.html",
            doctor=doctor,
            messages=messages
        )
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))

@doctor_bp.route("/doctor/patients")
@login_required
def doctor_patients():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor

        patients = doctor.patients 

        return render_template(
            "doctor_patientlist.html",
            doctor=doctor,
            patients=patients
        )
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))

@doctor_bp.route("/patients")
@login_required
def doctor_patientlist():
    # Assuming `current_user` is a Doctor
    patients = Patient.query.filter_by(doctor_id=current_user.doctor_id).all()
    return render_template("doctor_patientlist.html", patients=patients)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login_options")) 