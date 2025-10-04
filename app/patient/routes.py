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