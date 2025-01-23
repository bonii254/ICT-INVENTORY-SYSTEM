from marshmallow import fields, validate, validates, ValidationError, post_load
from app.extensions import ma
from app.models.v1 import Software
from datetime import datetime


class RegSoftwareSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    version = fields.Str(allow_none=True, validate=validate.Length(max=120))
    license_key = fields.Str(
        allow_none=True, validate=validate.Length(max=300))
    expiry_date = fields.Date(
        allow_none=True,
        error_messages={
            "invalid": "Invalid date format. Use 'YYYY-MM-DD'."
        }
    )

    @validates("name")
    def validate_name(self, value):
        if Software.query.filter(Software.name.ilike(value)).first():
            raise ValidationError(f"Software name '{value}' already exists.")

    @validates("expiry_date")
    def validate_expirydate(self, value):
        if value and value < datetime.utcnow().date():
            raise ValidationError("The 'expiry_date' cannot be in the past.")
