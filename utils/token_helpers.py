from functools import wraps
from flask import jsonify
import uuid

import logging
from flask_jwt_extended import get_jwt, get_jwt_identity
from datetime import datetime, timezone
from app.extensions import db, scheduler
from app.models.v1 import RevokedToken, User, ExternalMaintenance


def is_token_revoked(decoded_token):
    """
    Check if the token has been revoked.
    Used with Flask-JWT-Extended's `token_in_blocklist_loader`.
    """
    jti = decoded_token["jti"]
    token = RevokedToken.query.filter_by(jti=jti).first()
    return token is not None


def revoke_token():
    """
    Store a token in the revoked tokens table.
    """
    jti = get_jwt()["jti"]
    token_type = get_jwt()["type"]
    expires = datetime.fromtimestamp(get_jwt()["exp"], tz=timezone.utc)

    revoked = RevokedToken(
        jti=jti,
        token_type=token_type,
        expires_at=expires,
        revoked_at=datetime.now(timezone.utc)
    )
    db.session.add(revoked)
    db.session.commit()


def clear_expired_tokens():
    """
    Delete expired revoked tokens from the database.
    """
    now = datetime.now(timezone.utc)
    expired_tokens = RevokedToken.query.filter(
        RevokedToken.expires_at < now
    ).all()

    for token in expired_tokens:
        db.session.delete(token)

    db.session.commit()
    print(f"✅ Deleted {len(expired_tokens)} expired revoked tokens.")


def clear_expired_tokens_with_context(app):
    """
    Run cleanup inside the Flask app context.
    """
    with app.app_context():
        clear_expired_tokens()


def init_scheduler(app):
    try:
        scheduler.add_job(
            func=lambda: clear_expired_tokens_with_context(app),
            trigger="interval",
            hours=6,
            id="clear_revoked_tokens",
            replace_existing=True,
            max_instances=1,
        )
        app.logger.info("Scheduler job scheduled successfully.")
    except Exception as e:
        app.logger.warning(f"Scheduler job not started: {e}")
        
        
        
def smart_title(name, acronyms=None):
    """
    Capitalize each word in a string, but keep known acronyms fully uppercase.
    
    Args:
        name (str): Input string.
        acronyms (list): List of acronyms to preserve in uppercase.
    
    Returns:
        str: Properly capitalized string.
    """
    if acronyms is None:
        acronyms = ["ICT", "HR", "IT", "AI"]

    words = name.split()
    result = []
    for word in words:
        if word.upper() in acronyms:
            result.append(word.upper())
        else:
            result.append(word.capitalize())
    return " ".join(result)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        caller = db.session.get(User, get_jwt_identity())
        if not caller:
            return jsonify({"error": "Unauthorized"}), 401
        if getattr(caller.role, "name", "").upper() not in {"ADMIN", "SUPERADMIN", "IT_ADMIN"}:
            return jsonify({"error": "Admin privileges required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def generate_receipt_number(domain):
    """
    Generate a unique, traceable receipt number.
    Format: GDFCS-{DOMAIN}-{CATEGORY}-{YYYYMMDD}-{SHORTUUID}
    Example: GDFCS-ICT-LAPTOP-20251129-7F2A3B9C
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:8].upper()

    return f"GDFCS-{domain}{timestamp}-{short_uuid}"