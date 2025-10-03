from flask import Blueprint, render_template

doctor_bp = Blueprint("doctor", __name__, template_folder="templates")

@doctor_bp.route("/doctor")
def doctor_home():
    return render_template("doctor.html")

@doctor_bp.route("/doctor/appointments")
def doctor_appointments():
    return render_template("appointments.html")