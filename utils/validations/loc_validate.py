from marshmallow import fields, validate, validates, ValidationError
from app.extensions import ma
from app.models.v1 import Location


class RegLocSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    address = fields.Str(
        required=True, validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if Location.query.filter(Location.name.ilike(value)).first():
            raise ValidationError(f"Location name '{value}' already exists.")


class UpdateLocSchema(ma.Schema):
    name = fields.Str(validate=validate.Length(min=1, max=120))
    address = fields.Str(validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if value:
            if Location.query.filter(Location.name.ilike(value)).first():
                raise ValidationError(
                    f"Location name '{value}' already exists.")
