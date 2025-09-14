from flask import Blueprint, render_template


# Use flask blueprints to create modular sections for our website
# Will allow us to have different folders for patient, doctor, and admin portions of the website
main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/")
def index():
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

