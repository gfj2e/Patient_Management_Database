import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from flask import url_for

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
PORT_NUMBER = 587

def send_email(subject, body, to_email):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = EMAIL_ADDRESS
    message["To"] = to_email
    message.set_content(body)
    
    try:
        with smtplib.SMTP("smtp.gmail.com", PORT_NUMBER) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(message)
            print("Email sent via gmail...")
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    
# send_email("Hello World", "Hello World", "test-fj61d5oxd@srv1.mail-tester.com")

def send_reset_email(user_email, reset_link):
    subject = "Reset your CuraCloud password"
    body = f"""Hello,

    You requested a password reset for your CuraCloud account.

    Click the following link to reset your password:
    {reset_link}

    This link will expire in 1 hour.

    If you did not request this reset, please ignore this email.

    Best regards,
    The CuraCloud Team
    """
    return send_email(subject, body, user_email)