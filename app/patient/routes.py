from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..database.models import (Patient_Login, Appointment, Patient, Test_Result, 
                               TestStatus, Prescription, Billing)
from ..database.connection import db
from sqlalchemy import select
from datetime import datetime

patient_bp = Blueprint("patient", __name__, template_folder="templates")

@patient_bp.route("/patient")
@login_required
def patient_home():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        upcoming_appointments = db.session.execute(
            select(Appointment).where(Appointment.patient_id == patient.patient_id,
            Appointment.appointment_time >= datetime.now()
            ).order_by(Appointment.appointment_time)
        ).scalars().all()
        
        message_count = len(patient.messages)
        
        billing = db.session.execute(
            select(Billing).where(Billing.patient_id == patient.patient_id
            ).order_by(Billing.billing_date.asc())
        ).scalar()
        
        lab_results = db.session.execute(
            select(Test_Result).where(Test_Result.patient_id == patient.patient_id,
            Test_Result.test_status == TestStatus.COMPLETED
            ).order_by(Test_Result.result_time.desc())
        ).scalars().all()
        
        print(f"Patient ID: {patient.patient_id}")
        print(f"Lab results found: {len(lab_results)}")
        for result in lab_results:
            print(f"Result: {result.test_name}, Status: {result.test_status}, Date: {result.result_time}")
        
        patient_prescriptions = patient.prescriptions
        
        return render_template("patient_home.html", 
                               patient=patient,
                               patient_name=patient_name, 
                               upcoming_appointments=upcoming_appointments,
                               message_count=message_count,
                               billing=billing,
                               lab_results=lab_results,
                               patient_prescriptions=patient_prescriptions)
    else:
        flash("You must be logged in as a patient to view this page.", "danger")
        return redirect(url_for('auth.login'))

@patient_bp.route("/appointments")
@login_required
def appointments():
    return render_template("appointments.html")  

@patient_bp.route("/prescriptions")
@login_required
def prescriptions():
    return render_template("prescriptions.html")

@patient_bp.route("/billing")
@login_required
def billing():
    return render_template("billing.html")

@patient_bp.route("/lab-results")
@login_required
def lab_results():
    return render_template("lab_results.html")

@patient_bp.route("/messages")
@login_required
def messages():
    return render_template("messages.html")

@patient_bp.route("/patient_info")
@login_required
def patient_info():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        return render_template("patient_info.html", 
                             patient=patient,
                             patient_name=patient_name)
    else:
        flash("You must be logged in as a patient to view this page.", "danger")
        return redirect(url_for('auth.login'))