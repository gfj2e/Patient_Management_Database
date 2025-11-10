from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user, logout_user
from ..database.models import (Doctor_Login, Appointment, Patient, Message, 
                               PrescriptionRefillRequest, RefillStatus)
from ..database.connection import db
from sqlalchemy import select
from datetime import datetime, date


auth_bp = Blueprint("auth", __name__, template_folder="templates") 
doctor_bp = Blueprint("doctor", __name__, template_folder="templates")

@doctor_bp.route("/doctor")
@login_required
def doctor_home():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        doctor_name = f"{doctor.first_name} {doctor.last_name}"
        
        upcoming_appointments = db.session.execute(
            select(Appointment).where(Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time >= datetime.now()
            ).order_by(Appointment.appointment_time)
        ).scalars().all()
        
        patients = doctor.patients

        messages_count = len(doctor.messages)

        pending_refill_count = db.session.execute(
            select(PrescriptionRefillRequest)
            .where(
                PrescriptionRefillRequest.doctor_id == doctor.doctor_id,
                PrescriptionRefillRequest.status == RefillStatus.PENDING
            )
        ).scalars().all()
        pending_refill_count = len(pending_refill_count)

        return render_template("doctor_home.html", 
                               doctor=doctor, 
                               doctor_name=doctor_name, 
                               appointments=upcoming_appointments,
                               patients=list(patients),
                               messages_count=messages_count,
                               pending_refill_count=pending_refill_count
                               )
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))

@doctor_bp.route("/doctor/appointments")
@login_required
def doctor_appointments():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        
        todays_appointments = db.session.execute(
            select(Appointment).where(Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time.between(
                datetime.combine(date.today(), datetime.min.time()),
                datetime.combine(date.today(), datetime.max.time())
            )).order_by(Appointment.appointment_time)
        ).scalars().all()
        
        upcoming_appointments = db.session.execute(
            select(Appointment).where(Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time > datetime.combine(date.today(), datetime.max.time())
            ).order_by(Appointment.appointment_time)
        ).scalars().all()
        
        past_appointments = db.session.execute(
            select(Appointment).where(Appointment.doctor_id == doctor.doctor_id,
            Appointment.appointment_time < datetime.combine(date.today(), datetime.min.time())
            ).order_by(Appointment.appointment_time.desc())
        ).scalars().all()

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
    doctor = current_user.doctor
    patients = doctor.patients
    return render_template("doctor_patientlist.html", patients=patients)

@doctor_bp.route("/doctor/messages")
@login_required
def doctor_messages():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        messages = doctor.messages
        patients = doctor.patients
        
        return render_template("doctor_messages.html", doctor=doctor, messages=messages, patients=patients)
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))

@doctor_bp.route("/send_message", methods=["POST"])
@login_required
def send_message():
    patient_id = request.form.get("patient_id")
    content = request.form.get("content")

    if not patient_id or not content:
        flash("Please select a patient and enter a message.", "danger")
        return redirect(url_for("doctor.doctor_messages"))

    new_message = Message(
        content=content,
        sender_type="doctor",
        doctor_id=current_user.doctor_id,
        patient_id=int(patient_id)
    )
    db.session.add(new_message)
    db.session.commit()

    flash("Message sent successfully!", "success")
    return redirect(url_for("doctor.doctor_messages"))

@doctor_bp.route("/doctor/refills")
@login_required
def doctor_refills():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        
        pending_refills = db.session.execute(
            select(PrescriptionRefillRequest).where(
                PrescriptionRefillRequest.doctor_id == doctor.doctor_id,
                PrescriptionRefillRequest.status == RefillStatus.PENDING
            ).order_by(PrescriptionRefillRequest.request_date.asc())
        ).scalars().all()

        past_refills = db.session.execute(
            select(PrescriptionRefillRequest).where(
                PrescriptionRefillRequest.doctor_id == doctor.doctor_id,
                PrescriptionRefillRequest.status != RefillStatus.PENDING
            ).order_by(PrescriptionRefillRequest.request_date.desc())
        ).scalars().all()
    
        # return render_template("doctor_refills.html", doctor=doctor, refills=pending_refills)
        return render_template("doctor_refills.html", doctor=doctor, refill_requests=pending_refills, past_refills=past_refills )
    
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))

@doctor_bp.route("/doctor/handle_refill/<int:request_id>", methods=["POST"])
@login_required
def handle_refill(request_id):
    refill = PrescriptionRefillRequest.query.get_or_404(request_id)
    action = request.form.get("action")
    custom_notes = request.form.get("custom_notes") or ""

    doctor_name = f"{current_user.doctor.first_name} {current_user.doctor.last_name}"


    if action == "approve":
        refill.status = RefillStatus.APPROVED
        refill.notes = (
            f"Approved by Dr. {doctor_name} on {datetime.now().strftime('%b %d, %Y %I:%M %p')}."
            f"<br><strong>Message:</strong> {custom_notes}"
        )        
        flash("Refill approved successfully!", "success")

    elif action == "deny":
        refill.status = RefillStatus.DENIED
        refill.notes = (
            f"Denied by Dr. {doctor_name} on {datetime.now().strftime('%b %d, %Y %I:%M %p')}."
            f"<br><strong>Message:</strong> {custom_notes}"
        )
        flash("Refill denied.", "warning")

    db.session.commit()
    return redirect(url_for("doctor.doctor_refills"))

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login_options")) 