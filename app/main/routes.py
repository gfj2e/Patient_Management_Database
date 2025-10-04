from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from ..database.models import Patient_Login, Doctor_Login, Admin_Login

# Use flask blueprints to create modular sections for our website
# Will allow us to have different folders for patient, doctor, and admin portions of the website
main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if isinstance(current_user, Patient_Login):
            return redirect(url_for('patient.patient_home'))
        elif isinstance(current_user, Doctor_Login):
            return redirect(url_for('doctor.dashboard')) # Assuming you have a doctor dashboard
        elif isinstance(current_user, Admin_Login):
            return redirect(url_for('admin.dashboard')) # Assuming you have an admin dashboard
    return render_template("index.html")

@main_bp.route("/contact")
def contact():
    return render_template("contact.html")

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/services")
def services():
    return render_template("services.html")

