from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..database.models import Doctor_Login

doctor_bp = Blueprint("doctor", __name__, template_folder="templates")

@doctor_bp.route("/doctor")
@login_required
def doctor_home():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        return render_template("doctor_home.html", doctor=doctor)
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))

@doctor_bp.route("/doctor/appointments")
@login_required
def doctor_appointments():
    return render_template("appointments.html")