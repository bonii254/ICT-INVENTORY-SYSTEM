from marshmallow import validate, validates, ValidationError, fields, post_load 
from app.extensions import ma
from app.models.v1 import Status


class RegStatusSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    description = fields.Str(required=True)

    @validates("name")
    def validate_fields(self, value):
        if Status.query.filter(Status.name.ilike(value)).first():
            raise ValidationError(f"Status name '{value}' already exists.")

    @post_load
    def process_role(self, data, **kwargs):
        data['name'] = data['name'].capitalize()
        return data


class UpdatestatusSchema(ma.Schema):
    name = fields.Str(validate=validate.Length(min=1, max=120))
    description = fields.Str()

    @validates("name")
    def validate_fields(self, value):
        if value:
            if Status.query.filter(Status.name.ilike(value)).first():
                raise ValidationError(f"Status name '{value}' already exists.")
