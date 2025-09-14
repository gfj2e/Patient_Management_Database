from flask import Blueprint, render_template


# Use flask blueprints to create modular sections for our website
# Will allow us to have different folders for patient, doctor, and admin portions of the website
bp = Blueprint("main", __name__, template_folder="templates")

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/contact")
def contact():
    return render_template("contact.html")

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/services")
def services():
    return render_template("services.html")

