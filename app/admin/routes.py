import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..database.models import Admin_Login, Patient, Doctor, Billing, Appointment, Insurance
from ..database.connection import db
from sqlalchemy import select, func
from app.database.seed import SPECIALTIES
from datetime import date, datetime
from utils.logger import log_event
from ..database.models import ActivityLog


admin_bp = Blueprint("admin", __name__, template_folder="templates")

@admin_bp.route("/admin")
@login_required
def admin_home():
    if current_user.is_authenticated and isinstance(current_user, Admin_Login):
        patients_count = db.session.scalar(select(db.func.count()).select_from(Patient))
        doctors_count = db.session.scalar(select(db.func.count()).select_from(Doctor))
        billing_total_count = db.session.scalar(select(db.func.count()).select_from(Billing))

        return render_template(
            "admin_home.html",
            patients_count=patients_count,
            doctors_count=doctors_count,
            billing_total_count=billing_total_count
        )
    else:
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

@admin_bp.route("/admin/patients")
@login_required
def admin_patients():
    if not (current_user.is_authenticated and isinstance(current_user, Admin_Login)):
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

    patients = Patient.query.options(db.joinedload(Patient.doctors)).all()
    doctors = Doctor.query.all()

    return render_template("admin_patients.html", patients=patients, doctors=doctors)

@admin_bp.route("/add_patient", methods=["POST"])
@login_required
def add_patient():
    if not (current_user.is_authenticated and isinstance(current_user, Admin_Login)):
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone_number")
    dob_str = request.form.get("dob")
    gender = request.form.get("gender")
    address = request.form.get("address")

    doctor_ids = request.form.getlist("doctor_ids")  # from checkbox dropdown
    assigned_doctors = db.session.query(Doctor).filter(Doctor.doctor_id.in_(doctor_ids)).all()

    if dob_str:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        age = (date.today() - dob).days // 365
    else:
        dob = None
        age = 0

    patient_code = f"{first_name[:2].upper()}{last_name[:2].upper()}{int(datetime.now().timestamp())}"

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
        height=0.00,
        marriage_status="Single",
        race="OTHER_MIXED"
    )

    new_patient.doctors = assigned_doctors

    db.session.add(new_patient)
    db.session.commit()

    log_event(
    "add_patient",
    f"Added patient {new_patient.first_name} {new_patient.last_name}",
    target_type="patient",
    target_id=new_patient.patient_id
)

    flash("Patient added successfully!", "success")
    return redirect(url_for("admin.admin_patients"))


@admin_bp.route("/admin/edit_patient/<int:patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    if not (current_user.is_authenticated and isinstance(current_user, Admin_Login)):
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

    patient = db.get_or_404(Patient, patient_id)
    
    if request.method == "POST":
        patient.first_name = request.form.get("first_name")
        patient.last_name = request.form.get("last_name")
        patient.email = request.form.get("email")
        patient.phone_number = request.form.get("phone_number")
        patient.address = request.form.get("address")
        patient.gender = request.form.get("gender")
        dob_str = request.form.get("dob")
        if dob_str:
            patient.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

        doctor_ids = request.form.getlist("doctor_ids")
        assigned_doctors = db.session.query(Doctor).filter(Doctor.doctor_id.in_(doctor_ids)).all()
        patient.doctors = assigned_doctors

        db.session.commit()

        log_event(
    "edit_patient",
    f"Edited patient {patient.first_name} {patient.last_name}",
    target_type="patient",
    target_id=patient.patient_id
)

        flash("Patient information updated successfully!", "success")
        return redirect(url_for("admin.admin_patients"))

    return render_template("admin_edit_patient.html", patient=patient)

@admin_bp.route("/delete_patient/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):
    patient = db.get_or_404(Patient, patient_id)
    db.session.delete(patient)
    db.session.commit()

    log_event(
    "delete_patient",
    f"Deleted patient {patient.first_name} {patient.last_name}",
    target_type="patient",
    target_id=patient.patient_id
)

    flash("Patient deleted successfully!", "success")
    return redirect(url_for("admin.admin_patients"))

@admin_bp.route("/admin/doctors")
@login_required
def admin_doctors():
    if current_user.is_authenticated and isinstance(current_user, Admin_Login):
        doctors = db.session.execute(select(Doctor)).scalars().all()
        return render_template("admin_doctors.html", doctors=doctors,specialties=SPECIALTIES)
    else:
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))
    
@admin_bp.route("/add_doctor", methods=["POST"])
@login_required
def add_doctor():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    specialty = request.form.get("specialty")
    email = request.form.get("email")
    phone = request.form.get("phone")
    city = request.form.get("city")
    state = request.form.get("state")

    accepting_new = True if request.form.get("accepting_patients") == "on" else False

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
        is_accepting_new_patients=accepting_new
    )
    db.session.add(new_doctor)
    db.session.commit()

    log_event(
    "add_doctor",
    f"Added doctor {new_doctor.first_name} {new_doctor.last_name}",
    target_type="doctor",
    target_id=new_doctor.doctor_id
)

    flash("Doctor added successfully!", "success")
    return redirect(url_for("admin.admin_doctors"))

@admin_bp.route('/edit_doctor/<int:doctor_id>', methods=['POST'])
def edit_doctor(doctor_id):
    doctor = db.session.execute(
        select(Doctor).where(Doctor.doctor_id == doctor_id)
    ).scalar_one_or_none()

    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for('admin.admin_doctors'))

    try:
        doctor.first_name = request.form.get("first_name")
        doctor.last_name = request.form.get("last_name")
        doctor.specialty = request.form.get("specialty")
        doctor.email = request.form.get("email")
        doctor.phone_number = request.form.get("phone")
        doctor.city = request.form.get("city")
        doctor.state = request.form.get("state")
        doctor.accepting_patients = bool(request.form.get("accepting_patients"))

        db.session.commit()
        flash("Doctor information updated successfully!", "success")

    except Exception as e:
        db.session.rollback()
        print("EDIT DOCTOR ERROR:", e)
        flash("Failed to update doctor.", "danger")

    return redirect(url_for('admin.admin_doctors'))


@admin_bp.route("/delete_doctor/<int:doctor_id>", methods=["POST"])
def delete_doctor(doctor_id):
    doctor = db.get_or_404(Doctor, doctor_id)
    db.session.delete(doctor)
    db.session.commit()

    log_event(
    "delete_doctor",
    f"Deleted doctor {doctor.first_name} {doctor.last_name}",
    target_type="doctor",
    target_id=doctor.doctor_id
)

    flash("Doctor deleted successfully.", "info")
    return redirect(url_for("admin.admin_doctors"))

@admin_bp.route("/admin/billing")
@login_required
def admin_billing():
    if current_user.is_authenticated and isinstance(current_user, Admin_Login):

        billing_records = db.session.execute(select(Billing)).scalars().all()
        
        patients = db.session.execute(select(Patient)).scalars().all()
        return render_template("admin_billing.html", billing_records=billing_records, patients=patients)
    else:
        flash("You must be logged in as an admin to view this page.")
        return redirect(url_for("auth.login"))

@admin_bp.route("/add_billing", methods=["POST"])
@login_required
def add_billing():
    patient_id = request.form.get("patient_id")
    amount = request.form.get("amount")
    billing_date = request.form.get("billing_date")
    notes = request.form.get("notes")

    if not all([patient_id, amount, billing_date]):
        flash("All required fields must be filled.", "danger")
        return redirect(url_for("admin.admin_billing"))

    billing_entry = Billing(
        patient_id=patient_id,
        billing_amount=amount,
        billing_date=datetime.strptime(billing_date, "%Y-%m-%d").date(),
        notes=notes
    )
    db.session.add(billing_entry)
    db.session.commit()

    log_event(
    "add_billing",
    f"Added billing entry for patient ID {patient_id}",
    target_type="billing",
    target_id=billing_entry.billing_id
)

    flash("Billing entry added successfully!", "success")
    return redirect(url_for("admin.admin_billing"))

@admin_bp.route("/admin/logs")
@login_required
def system_logs():
    logs = db.session.execute(
        select(ActivityLog).order_by(ActivityLog.timestamp.desc())
    ).scalars().all()

    return render_template("admin_logs.html", logs=logs)

@admin_bp.route("/admin/appointments")
@login_required
def admin_appointments():
    if not (current_user.is_authenticated and isinstance(current_user, Admin_Login)):
        flash("You must be logged in as an admin to view appointments.")
        return redirect(url_for("auth.login"))

    appointments = Appointment.query.options(
        db.joinedload(Appointment.patient),
        db.joinedload(Appointment.doctor)
    ).all()

    patients = Patient.query.all()
    doctors = Doctor.query.all()

    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        patients=patients,
        doctors=doctors
    )

@admin_bp.route("/add_appointment", methods=["POST"])
@login_required
def add_appointment():
    patient_id = request.form.get("patient_id")
    doctor_id = request.form.get("doctor_id")
    appointment_time = request.form.get("appointment_time")
    clinic = request.form.get("clinic_name")
    city = request.form.get("city")
    state = request.form.get("state")

    if not all([patient_id, doctor_id, appointment_time, clinic, city, state]):
        flash("All fields are required.", "danger")
        return redirect(url_for("admin.admin_appointments"))

    new_appt = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_time=datetime.strptime(appointment_time, "%Y-%m-%dT%H:%M"),
        clinic_name=clinic,
        city=city,
        state=state
    )

    db.session.add(new_appt)
    db.session.commit()

    log_event(
        "add_appointment",
        f"Added appointment for patient {patient_id}",
        target_type="appointment",
        target_id=new_appt.appointment_id
    )

    flash("Appointment added successfully!", "success")
    return redirect(url_for("admin.admin_appointments"))

@admin_bp.route("/edit_appointment/<int:appointment_id>", methods=["POST"])
@login_required
def edit_appointment(appointment_id):

    appt = Appointment.query.get_or_404(appointment_id)

    appt.patient_id = request.form.get("patient_id")
    appt.doctor_id = request.form.get("doctor_id")
    appt.appointment_time = datetime.strptime(
        request.form.get("appointment_time"), "%Y-%m-%dT%H:%M"
    )
    appt.clinic_name = request.form.get("clinic_name")
    appt.city = request.form.get("city")
    appt.state = request.form.get("state")

    db.session.commit()

    log_event(
        "edit_appointment",
        f"Edited appointment {appointment_id}",
        target_type="appointment",
        target_id=appointment_id
    )

    flash("Appointment updated successfully!", "success")
    return redirect(url_for("admin.admin_appointments"))

@admin_bp.route("/delete_appointment/<int:appointment_id>", methods=["POST"])
@login_required
def delete_appointment(appointment_id):

    appt = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appt)
    db.session.commit()

    log_event(
        "delete_appointment",
        f"Deleted appointment {appointment_id}",
        target_type="appointment",
        target_id=appointment_id
    )

    flash("Appointment deleted.", "info")
    return redirect(url_for("admin.admin_appointments"))