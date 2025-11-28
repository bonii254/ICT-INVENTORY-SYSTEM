from flask import current_app
import threading
from flask_mail import Message
from app.extensions import mail


def _send_async_email(app, msg):
    """Send email safely in a background thread with app context."""
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, html_body):
    """Generic async email sender."""
    msg = Message(subject=subject, recipients=recipients)
    msg.html = html_body
    app = current_app._get_current_object()
    thread = threading.Thread(target=_send_async_email, args=(app, msg))
    thread.start()


def send_welcome_email(user_fullname, user_email, raw_password, app_name="Fresha Inventory System"):
    """Send welcome email for newly created users."""
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">
        <h2 style="color:#004080;">Welcome to <span style="color:#0080ff;">{app_name}</span></h2>
        <p>Dear <strong>{user_fullname}</strong>,</p>
        <p>Your account has been successfully created in the <strong>{app_name}</strong>.</p>
        <p><strong>Login Credentials:</strong></p>
        <ul>
            <li>Email: <strong>{user_email}</strong></li>
            <li>Temporary Password: <strong>{raw_password}</strong></li>
        </ul>
        <p style="color:#d9534f;"><strong>Important:</strong> Please change your password immediately after your first login.</p>
        <p>Regards,<br><strong>{app_name} Team</strong></p>
        <hr>
        <small style="color:#888;">This is an automated message. Please do not reply.</small>
    </div>
    """
    send_email(f"Welcome to {app_name}", [user_email], html_body)


def send_password_changed_email(user_fullname, user_email, app_name="Fresha Inventory System"):
    """Send email notifying user that their password has been changed."""
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">
        <h2 style="color:#004080;">Password Update Notification</h2>
        <p>Dear <strong>{user_fullname}</strong>,</p>
        <p>Your password for <strong>{app_name}</strong> has been updated.</p>
        <p style="color:#d9534f;"><strong>Important:</strong> If you did not perform this change, please contact your administrator immediately.</p>
        <p>Regards,<br><strong>{app_name} Team</strong></p>
        <hr>
        <small style="color:#888;">This is an automated message. Please do not reply.</small>
    </div>
    """
    send_email(f"{app_name} - Password Changed", [user_email], html_body)