from datetime import datetime, timezone
from flask_socketio import join_room, emit
from flask_login import current_user
from app.database.models import Message, Doctor, Patient
from app.database.connection import db

def init_socketio_events(socketio):

    @socketio.on("join_room")
    def handle_join_room(data):
        room = data["room"]
        join_room(room)
        print(f"User {current_user.id} joined room {room}")

    @socketio.on("send_message")
    def handle_send_message(data):
        room = data["room"]
        message = data["message"]
        sender_type = data["sender_type"]
        doctor_id = int(data["doctor_id"])
        patient_id = int(data["patient_id"])

        timestamp = datetime.now(timezone.utc)

        new_msg = Message(
            content = message,
            sender_type = sender_type,
            doctor_id = doctor_id,
            patient_id = patient_id
        )

        db.session.add(new_msg)
        db.session.commit()
        
        emit("receive_message", {
            "message": message,
            "sender_type": sender_type,
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "timestamp": timestamp.isoformat()
        }, to = room)