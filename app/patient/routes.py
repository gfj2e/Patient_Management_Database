from flask import Blueprint, render_template

patient_bp = Blueprint("patient", __name__, template_folder="templates")

@patient_bp.route("/patient")
def patient_home():
    return render_template("patient_home.html")  

@patient_bp.route("/appointments")
def appointments():
    return render_template("appointments.html")  