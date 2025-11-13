from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, make_response
from flask_login import login_required, current_user
from ..database.models import (Patient_Login, Appointment, Patient, Message, Test_Result, 
                               TestStatus, Prescription, Billing, Doctor, PrescriptionRefillRequest, RefillStatus)
from ..database.connection import db
from sqlalchemy import select
from datetime import datetime, date
from utils.logger import log_event
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO


patient_bp = Blueprint("patient", __name__, template_folder="templates")

@patient_bp.route("/patient")
@login_required
def patient_home():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        upcoming_appointments = db.session.execute(
            select(Appointment).where(Appointment.patient_id == patient.patient_id,
            Appointment.appointment_time >= datetime.now()
            ).order_by(Appointment.appointment_time)
        ).scalars().all()
        
        message_count = len(patient.messages)
        
        billing = db.session.execute(
            select(Billing).where(Billing.patient_id == patient.patient_id
            ).order_by(Billing.billing_date.asc())
        ).scalar()
        
        lab_results = db.session.execute(
            select(Test_Result).where(Test_Result.patient_id == patient.patient_id,
            Test_Result.test_status == TestStatus.COMPLETED
            ).order_by(Test_Result.result_time.desc())
        ).scalars().all()
        
        print(f"Patient ID: {patient.patient_id}")
        print(f"Lab results found: {len(lab_results)}")
        for result in lab_results:
            print(f"Result: {result.test_name}, Status: {result.test_status}, Date: {result.result_time}")
        
        patient_prescriptions = patient.prescriptions
        
        return render_template("patient_home.html", 
                               patient=patient,
                               patient_name=patient_name, 
                               upcoming_appointments=upcoming_appointments,
                               message_count=message_count,
                               billing=billing,
                               lab_results=lab_results,
                               patient_prescriptions=patient_prescriptions)
    else:
        flash("You must be logged in as a patient to view this page.", "danger")
        return redirect(url_for('auth.login'))

@patient_bp.route("/appointments")
@login_required
def appointments():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        
        # Upcoming appointments
        upcoming_appointments = db.session.execute(
            select(Appointment).where(Appointment.patient_id == patient.patient_id,
            Appointment.appointment_time >= datetime.now()
            ).order_by(Appointment.appointment_time)
        ).scalars().all()
    
        # Appointment history
        past_appointments = db.session.execute(
            select(Appointment).where(Appointment.patient_id == patient.patient_id,
            Appointment.appointment_time < datetime.combine(date.today(), datetime.min.time())
            ).order_by(Appointment.appointment_time.desc())
        ).scalars().all()
    
        # Doctors 
        doctors = db.session.execute(select(Doctor)).scalars().all()
    
        return render_template("appointments.html",
                           patient=patient,
                           upcoming_appointments=upcoming_appointments,
                           past_appointments=past_appointments,
                           doctors=doctors)  
    else:
        flash("You must be logged in to view this page")
        return redirect(url_for('auth.login'))

@patient_bp.route("/prescriptions")
@login_required
def prescriptions():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        
        prescriptions = patient.prescriptions
        
        refills = patient.prescription_refill_requests
    
        return render_template("prescriptions.html",
                               patient=patient,
                               prescriptions=prescriptions,
                               refills=refills)
    else:
        flash("You must be logged in to view this page")
        return redirect(url_for('auth.login'))

@patient_bp.route("/billing")
@login_required
def billing():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        
        billing = db.session.execute(
            select(Billing).where(Billing.patient_id == patient.patient_id
            ).order_by(Billing.billing_date.asc())
        ).scalar()
    
        return render_template("billing.html",
                            patient=patient,
                            billing=billing)
    else:
        flash("You must be logged in to view this page")
        return redirect(url_for('auth.login'))

@patient_bp.route("/lab-results")
@login_required
def lab_results():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        
        lab_results = db.session.execute(
            select(Test_Result).where(Test_Result.patient_id == patient.patient_id
            ).order_by(Test_Result.result_time.asc())
        ).scalars().all()
        
        abnormal_results = db.session.execute(
            select(Test_Result).where(Test_Result.patient_id == patient.patient_id,
            Test_Result.test_status == TestStatus.ABNORMAL)
        ).scalars().all()
            
        return render_template("lab_results.html",
                            lab_results=lab_results,
                            abnormal_results=abnormal_results)
        
    else:
        flash("You must be logged in to view this page")
        return redirect(url_for('auth.login'))

@patient_bp.route("/messages")
@login_required
def patient_messages():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        messages = patient.messages
        doctors = patient.doctors
        # doctors = [doctor] if doctor else []
        
        return render_template("messages.html", patient = patient, messages = messages, doctors = doctors)
    else:
        flash("You must be logged in as a doctor to view this page")
        return redirect(url_for('auth.login'))

@patient_bp.route("/send_message", methods = ["POST"])
@login_required
def send_message():
    doctor_id = request.form.get("doctor_id")
    content = request.form.get("content")

    if not doctor_id or not content:
        flash("Please select a doctor and enter a message.", "danger")
        return redirect(url_for("patient.patient_messages"))
    
    new_message = Message(
        content = content,
        sender_type = "patient",
        patient_id = current_user.patient_id,
        doctor_id = int(doctor_id)
    )
    db.session.add(new_message)
    db.session.commit()

    log_event(
        "patient_message_send",
        f"Patient {current_user.id} sent a message to doctor {doctor_id}",
        target_type="doctor",
        target_id=doctor_id
    )

    flash("Message sent successfully!", "success")
    return redirect(url_for("patient.patient_messages"))

@patient_bp.route("/patient_info")
@login_required
def patient_info():
    if current_user.is_authenticated and isinstance(current_user, Patient_Login):
        patient = current_user.patient
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        return render_template("patient_info.html", 
                                patient=patient,
                                patient_name=patient_name)
    else:
        flash("You must be logged in as a patient to view this page.", "danger")
        return redirect(url_for('auth.login'))
    
@patient_bp.route("/request_refill", methods=["POST"])
@login_required
def request_refill():
    if not current_user.is_authenticated and isinstance(current_user, Patient_Login):
        return jsonify({"success": False, "message": "Authentication error."}), 403
    
    patient = current_user.patient
    prescription_id = request.form.get("prescription_id")
    notes = request.form.get("notes", "")
    
    if not prescription_id:
        return jsonify({"success": False, "message": "Prescription ID is missing."}), 400
    
    prescription = db.session.get(Prescription, int(prescription_id))
    if not prescription or prescription.patient_id != patient.patient_id:
        return jsonify({"success": False, "message": "Invalid prescription selected"}), 403
    
    new_refill_request = PrescriptionRefillRequest(
        patient=patient.patient_id,
        doctor_id=prescription.doctor_id,
        prescription_id=prescription.prescription_id,
        status=RefillStatus.PENDING,
        notes=notes
    )

    db.session.add(new_refill_request)
    db.session.commit()

    log_event(
        "refill_requested",
        f"Patient {current_user.id} requested refill for prescription {prescription_id}",
        target_type="prescription",
        target_id=prescription_id
    )

    flash("Refill requjest successfully submitted", "success")
    
    return jsonify({"success": True, "message": "Refill request submitted"})

@patient_bp.route("/get-lab-results-json")
@login_required
def get_lab_results_json():
    # get all lab results for the current patient
    if not (current_user.is_authenticated and isinstance(current_user, Patient_Login)):
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    patient = current_user.patient
    lab_results = db.session.execute(
        select(Test_Result).where(Test_Result.patient_id == patient.patient_id)
        .order_by(Test_Result.result_time.desc())
    ).scalars().all()
    
    results_data = []
    for result in lab_results:
        results_data.append({
            "test_id": result.test_id,
            "test_name": result.test_name,
            "ordered_date": result.ordered_date.strftime('%m/%d/%Y') if result.ordered_date else "N/A",
            "result_time": result.result_time.strftime('%m/%d/%Y') if result.result_time else "N/A",
            "result_value": result.result_value or "N/A",
            "unit_of_measure": result.unit_of_measure or "N/A",
            "reference_range": result.reference_range or "N/A",
            "test_status": result.test_status.value,
            "result_notes": result.result_notes or ""
        })
    
    return jsonify({"success": True, "results": results_data})

@patient_bp.route("/download-lab-report/<int:test_id>")
@login_required
def download_lab_report(test_id):
    # Download a lab result as PDF
    if not (current_user.is_authenticated and isinstance(current_user, Patient_Login)):
        return redirect(url_for('auth.login'))
    
    patient = current_user.patient
    
    # Ensure the test result belongs to the patient
    test_result = db.session.execute(
        select(Test_Result).where(
            Test_Result.test_id == test_id,
            Test_Result.patient_id == patient.patient_id
        )
    ).scalar()
    
    if not test_result:
        flash("Lab result not found", "danger")
        return redirect(url_for("patient.lab_results"))
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=1
    )
    story.append(Paragraph("CuraCloud Lab Result Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient information
    patient_info_style = ParagraphStyle(
        'PatientInfo',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12
    )
    story.append(Paragraph(f"<b>Patient Name:</b> {patient.first_name} {patient.last_name}", patient_info_style))
    story.append(Paragraph(f"<b>Patient ID:</b> {patient.patient_code}", patient_info_style))
    story.append(Paragraph(f"<b>Date of Birth:</b> {patient.dob.strftime('%m/%d/%Y')}", patient_info_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Test details
    test_header_style = ParagraphStyle(
        'TestHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12
    )
    story.append(Paragraph("Test Results", test_header_style))
    
    test_data = [
        ['Test Name', test_result.test_name],
        ['Test Status', test_result.test_status.value],
        ['Ordered Date', test_result.ordered_date.strftime('%m/%d/%Y') if test_result.ordered_date else 'N/A'],
        ['Result Date', test_result.result_time.strftime('%m/%d/%Y %I:%M %p') if test_result.result_time else 'N/A'],
        ['Result Value', test_result.result_value or 'N/A'],
        ['Unit of Measure', test_result.unit_of_measure or 'N/A'],
        ['Reference Range', test_result.reference_range or 'N/A'],
    ]
    
    test_table = Table(test_data, colWidths=[2.5*inch, 3.5*inch])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Notes if present
    if test_result.result_notes:
        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12
        )
        story.append(Paragraph("Clinical Notes", notes_style))
        notes_content_style = ParagraphStyle(
            'NotesContent',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12
        )
        story.append(Paragraph(test_result.result_notes, notes_content_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%m/%d/%Y at %I:%M %p')}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Reset buffer position
    pdf_buffer.seek(0)
    
    # Log the download action
    log_event(
        "lab_result_downloaded",
        f"Patient {current_user.id} downloaded lab result {test_id}",
        target_type="test_result",
        target_id=test_id
    )
    
    # Return PDF file
    filename = f"Lab_Result_{test_result.test_name}_{test_result.ordered_date.strftime('%m%d%Y')}.pdf"
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )