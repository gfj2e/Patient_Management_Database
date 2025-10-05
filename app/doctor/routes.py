from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..database.models import Doctor_Login
from flask_login import logout_user

auth_bp = Blueprint("auth", __name__, template_folder="templates")  # make sure this exists
doctor_bp = Blueprint("doctor", __name__, template_folder="templates")

@doctor_bp.route("/doctor")
@login_required
def doctor_home():
    if current_user.is_authenticated and isinstance(current_user, Doctor_Login):
        doctor = current_user.doctor
        doctor_name = f"{doctor.first_name} {doctor.last_name}"
        return render_template("doctor_home.html", doctor=doctor, doctor_name=doctor_name)
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))



@doctor_bp.route("/doctor/appointments")
@login_required
def doctor_appointments():
    return render_template("appointments.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login_options"))  # Redirect to your login options page 