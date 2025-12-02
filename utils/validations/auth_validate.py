from marshmallow import (
    fields, validate, validates, post_load, ValidationError, validates_schema)
from app.extensions import ma, db
from app.extensions import bcrypt
from app.models.v1 import User, Role, Department


class RegUserSchema(ma.Schema):
    fullname = fields.Str(
        required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    role_id = fields.Integer(required=True)
    department_id = fields.Integer(required=True)
    payroll_no = fields.Str(required=True)
    is_active = fields.Integer(required=False)

    @validates('email')
    def validate_email(self, value):
        """Check if the email already exists in the database."""
        if User.query.filter_by(email=value).first():
            raise ValidationError("Email already registered.")
        
    @validates('payroll_no')
    def validate_payroll_no(self, value):
        """check if payroll number/id is unique"""
        if User.query.filter_by(payroll_no=value).first():
            raise ValidationError("Invalid payroll no")

    @validates('role_id')
    def validate_role_id(self, value):
        if not Role.query.get(value):
            raise ValidationError(f"Role with id {value} does not exist.")

    @validates('department_id')
    def validate_department_id(self, value):
        if not Department.query.get(value):
            raise ValidationError(
                f"Department with id {value} does not exist.")

    @post_load
    def process_fields(self, data, **kwargs):
        """normalize fullname and email."""
        if 'fullname' in data and data['fullname']:
            data['fullname'] = data['fullname'].title()
        if 'email' in data and data['email']:
            data['email'] = data['email'].lower()
        return data


class LoginSchema(ma.Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True)

    @validates('email')
    def validate_email_exists(self, value):
        """Check if the email exists in the database."""
        user = User.query.filter_by(email=value).first()
        if not user:
            raise ValidationError("Email not found in the database.")


class UpdateUserSchema(ma.Schema):
    fullname = fields.Str(
        required=False, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=False, validate=validate.Length(max=120))
    department = fields.Str(required=False, validate=validate.Length(max=60))
    role_id = fields.Integer(required=False)
    payroll_no = fields.Integer(required=False)
    department_id = fields.Integer(required=False)
    domai_id = fields.Integer(required=False)
    is_active = fields.Integer(required=False)

    @validates('email')
    def validate_email(self, value):
        """Check if the email already exists in the database."""
        if value:
            if User.query.filter_by(email=value).first():
                raise ValidationError("Email already registered.")

    @validates('role_id')
    def validate_role_id(self, value):
        if value:
            if not db.session.get(Role, value):
                raise ValidationError(f"Role with id {value} does not exist.")

    @validates('department_id')
    def validate_department_id(self, value):
        if value:
            if not db.session.get(Department, value):
                raise ValidationError(
                    f"Department with id {value} does not exist.")
    @post_load
    def process_fields(self, data, **kwargs):
        """Normalize fullname and email before updating."""
        if 'fullname' in data and data['fullname']:
            data['fullname'] = data['fullname'].title()
        if 'email' in data and data['email']:
            data['email'] = data['email'].lower()
        return data
                
                
class UpdatePasswordSchema(ma.Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True)
    confirm_password = fields.String(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get("new_password") != data.get("confirm_password"):
            raise ValidationError("Passwords must match.", field_name="confirm_password")