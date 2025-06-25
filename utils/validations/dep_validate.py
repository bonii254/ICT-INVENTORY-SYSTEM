import re
from marshmallow import ( 
    fields, validate, validates, post_load, ValidationError)
from app.extensions import ma
from app.models.v1 import Department


class RegDepSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if Department.query.filter(Department.name.ilike(value)).first():
            raise ValidationError(f"Department name '{value}' already exists.")
        if not value.strip():
            raise ValidationError(
                "Department name cannot be empty or just whitespace.")
        if not re.match(r'^[A-Za-z0-9 ]+$', value):
            raise ValidationError(
                "Department name cannot contain special characters.")


class UpdateDepSchema(ma.Schema):
    name = fields.Str(required=True, validate=fields.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if value:
            if Department.query.filter(Department.name.ilike(value)).first():
                raise ValidationError(
                    f"Department name '{value}' already exists."
                )
            if not value.strip():
                raise ValidationError(
                    "Department name cannot be empty or just whitespace.")
            if not re.match(r'^[A-Za-z0-9 ]+$', value):
                raise ValidationError(
                    "Department name cannot contain special characters.")
