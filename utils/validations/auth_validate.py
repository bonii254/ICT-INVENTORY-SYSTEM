from marshmallow import (
    Schema, fields, validate, validates, post_load, ValidationError)
from app.extensions import ma
from datetime import datetime
from app.extensions import bcrypt
from app.models.v1 import User, Role, Department


class RegUserSchema(ma.Schema):
    fullname = fields.Str(
        required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(
        required=True, validate=validate.Length(
            min=6, error="Password must be at least 6 characters long."))
    role_id = fields.Integer(required=True)
    department_id = fields.Integer(required=True)

    @validates('email')
    def validate_email(self, value):
        """Check if the email already exists in the database."""
        if User.query.filter_by(email=value).first():
            raise ValidationError("Email already registered.")

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
    def hash_password(self, data, **kwargs):
        """Hash the password before saving the user to the database."""
        data['password'] = bcrypt.generate_password_hash(
            data['password']).decode('utf-8')
        return data


class LoginSchema(ma.Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True)

    @post_load
    def validate_email_exists(self, data, **kwargs):
        """Check if the email exists in the database."""
        email = data.get('email')
        user = User.query.filter_by(email=email).first()
        if not user:
            raise ValidationError("Email not found in the database.")
        return data


class UpdateUserSchema(ma.Schema):
    fullname = fields.Str(
        required=False, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=False, validate=validate.Length(max=120))
    department = fields.Str(required=False, validate=validate.Length(max=60))
    role_id = fields.Integer(required=False)
    department_id = fields.Integer(required=False)

    @validates('email')
    def validate_email(self, value):
        """Check if the email already exists in the database."""
        if value:
            if User.query.filter_by(email=value).first():
                raise ValidationError("Email already registered.")

    @validates('role_id')
    def validate_role_id(self, value):
        if value:
            if not Role.query.get(value):
                raise ValidationError(f"Role with id {value} does not exist.")

    @validates('department_id')
    def validate_department_id(self, value):
        if value:
            if not Department.query.get(value):
                raise ValidationError(
                    f"Department with id {value} does not exist.")
