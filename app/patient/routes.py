from flask import Blueprint, render_template

patient_bp  = Blueprint("patient", __name__, template_folder="templates")

@patient_bp.route("/patient")
def patient():
    return render_template("patient_home.html")