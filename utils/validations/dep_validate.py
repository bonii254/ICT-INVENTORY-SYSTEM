from marshmallow import (
    Schema, fields, validate, validates, post_load, ValidationError)
from app.extensions import ma
from app.models.v1 import Department


class RegDepSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if Department.query.filter(Department.name.ilike(value)).first():
            raise ValidationError(f"Department name '{value}' already exists.")


class UpdateDepSchema(ma.Schema):
    name = fields.Str(validate=fields.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if value:
            if Department.query.filter(Department.name.ilike(value)).first():
                raise ValidationError(
                    f"Department name '{value}' already exists."
                )
