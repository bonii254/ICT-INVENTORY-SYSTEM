from flask import g
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models import User

def register_request_hooks(app):
    """Attach user and domain context before each request."""
    @app.before_request
    def load_current_user():
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = db.session.get(User, user_id)
                g.current_user = user
                g.domain_id = user.domain_id if user else None
            else:
                g.current_user = None
                g.domain_id = None
        except Exception:
            g.current_user = None
            g.domain_id = None