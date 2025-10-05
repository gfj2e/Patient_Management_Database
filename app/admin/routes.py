from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..database.models import Admin_Login, Patient, Doctor, Billing

admin_bp = Blueprint("admin", __name__, template_folder="templates")

@admin_bp.route("/admin")
@login_required
def admin_home():
    if current_user.is_authenticated and isinstance(current_user, Admin_Login):
        patients_count = Patient.query.count()
        doctors_count = Doctor.query.count()
        # billing_pending_count = Billing.query.filter_by(status="Pending").count()
        billing_total_count = Billing.query.count()


        return render_template(
            "admin_home.html",
            patients_count=patients_count,
            doctors_count=doctors_count,
            # billing_pending_count=billing_pending_count,
            billing_total_count=billing_total_count
        )
    else:
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

@admin_bp.route("/admin/patients")
@login_required
def admin_patients():
    if current_user.is_authenticated and isinstance(current_user, Admin_Login):
        patients = Patient.query.all()
        return render_template("admin_patients.html", patients=patients)
    else:
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

@admin_bp.route("/admin/doctors")
@login_required
def admin_doctors():
    if current_user.is_authenticated and isinstance(current_user, Admin_Login):
        doctors = Doctor.query.all()
        return render_template("admin_doctors.html", doctors=doctors)
    else:
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

@admin_bp.route("/admin/billing")
@login_required
def admin_billing():
    if current_user.is_authenticated and isinstance(current_user, Admin_Login):
        billing_records = Billing.query.all()
        return render_template("admin_billing.html", billing_records=billing_records)
    else:
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

@admin_bp.route("/admin/patients")
@login_required
def patients():
    patients = Patient.query.all()
    return render_template("admin_patients.html", patients=patients)


