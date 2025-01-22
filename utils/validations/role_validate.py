from marshmallow import (
    fields, validate, validates, post_load, ValidationError)
from app.extensions import ma
from app.models.v1 import Role


class RegRoleSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    permissions = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^(\w+(,\w+)*)?$",
            error="Permissions must be a comma-separated list of words."
        )
    )

    @validates("name")
    def validate_name(self, value):
        if Role.query.filter(Role.name.ilike(value)).first():
            raise ValidationError(f"Role name '{value}' already exists.")

    @post_load
    def process_role(self, data, **kwargs):
        data['name'] = data['name'].capitalize()
        return Role(**data)


class UpdateRoleSchema(ma.Schema):
    name = fields.Str(validate=fields.Length(min=1, max=120))
    permissions = fields.Str(
        validate=validate.Regexp(
            r"^(\w+(,\w+)*)?$",
            error="Permissions must be a comma-separated list of words."
        )
    )

    @validates("name")
    def validate_name(self, value):
        # Ensure name is unique (case-insensitive)
        if value:
            if Role.query.filter(Role.name.ilike(value)).first():
                raise ValidationError(f"Role name '{value}' already exists.")
