from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..database.models import Patient_Login


patient_bp = Blueprint("patient", __name__, template_folder="templates")

@patient_bp.route("/patient")
@login_required
def patient_home():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        return render_template("patient_home.html", patient=patient)
    else:
        flash("You must be logged in as a patient to view this page.", "danger")
        return redirect(url_for('auth.login'))

@patient_bp.route("/appointments")
@login_required
def appointments():
    return render_template("appointments.html")  

@patient_bp.route("/prescriptions")
def prescriptions():
    return render_template("prescriptions.html")

@patient_bp.route("/billing")
def billing():
    return render_template("billing.html")

@patient_bp.route("/lab-results")
def lab_results():
    return render_template("lab_results.html")

@patient_bp.route("/messages")
def messages():
    return render_template("messages.html")

@patient_bp.route("/patient_info")
def patient_info():
    return render_template("patient_info.html")