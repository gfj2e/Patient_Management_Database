from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..database.models import Admin_Login, Patient, Doctor, Billing
from ..database.connection import db
from app.database.seed import SPECIALTIES
from datetime import date, datetime




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
        return render_template("admin_doctors.html", doctors=doctors,specialties=SPECIALTIES)
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


@admin_bp.route("/add_doctor", methods=["POST"])
def add_doctor():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    specialty = request.form.get("specialty")
    email = request.form.get("email")
    phone = request.form.get("phone")
    city = request.form.get("city")
    state = request.form.get("state")

    if not all([first_name, last_name, email]):
        flash("First name, last name, and email are required.", "danger")
        return redirect(url_for("admin.admin_doctors"))

    new_doctor = Doctor(
        first_name=first_name,
        last_name=last_name,
        specialty=specialty,
        state=state,
        city=city,
        phone_number=phone,
        email=email,
        is_accepting_new_patients=True
    )
    db.session.add(new_doctor)
    db.session.commit()

    flash("Doctor added successfully!", "success")
    return redirect(url_for("admin.admin_doctors"))


@admin_bp.route("/delete_doctor/<int:doctor_id>", methods=["POST"])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash("Doctor deleted successfully.", "info")
    return redirect(url_for("admin.admin_doctors"))

@admin_bp.route("/add_patient", methods=["POST"])
def add_patient():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form.get("email")
    phone = request.form.get("phone_number")
    dob_str = request.form.get("dob")
    gender = request.form.get("gender")
    address = request.form.get("address")

    # generate next patient_code
    last_patient = Patient.query.order_by(Patient.patient_id.desc()).first()
    next_id = (last_patient.patient_id + 1) if last_patient else 1
    patient_code = f"P{next_id:04d}"

    # Convert DOB string to date
    dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

    # Compute age
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    # Default fallback values
    height = 0
    marriage_status = "Single"
    race = "OTHER_MIXED"

    default_doctor = Doctor.query.first()
    doctor_id = default_doctor.doctor_id if default_doctor else None

    new_patient = Patient(
        patient_code=patient_code,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone,
        dob=dob,
        age=age,
        gender=gender,
        address=address,
        height=height,
        marriage_status=marriage_status,
        race=race,
        doctor_id=doctor_id
    )

    db.session.add(new_patient)
    db.session.commit()
    flash("Patient added successfully!", "success")
    return redirect(url_for("admin.admin_patients"))

@admin_bp.route("/delete_patient/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted successfully!", "success")
    return redirect(url_for("admin.admin_patients"))