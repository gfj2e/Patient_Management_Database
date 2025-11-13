from app.database.connection import db
from app.database.models import ActivityLog
from flask_login import current_user
from datetime import datetime

def log_event(action_type, description, target_type=None, target_id=None):

    actor_role = "system"
    actor_id = None

    if hasattr(current_user, "id"):
        actor_id = current_user.id

        classname = current_user.__class__.__name__

        if classname == "Admin_Login":
            actor_role = "admin"
        elif classname == "Doctor_Login":
            actor_role = "doctor"
        elif classname == "Patient_Login":
            actor_role = "patient"

    log = ActivityLog(
        action_type=action_type,
        actor_role=actor_role,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        description=description,
    )

    db.session.add(log)
    db.session.commit()
