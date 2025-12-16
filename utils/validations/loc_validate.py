from marshmallow import fields, validate, validates, ValidationError 
from app.extensions import ma, db
from app.models.v1 import Location, User
from flask_jwt_extended import get_jwt_identity


current_user = db.session.get(User, get_jwt_identity())


class RegLocSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    address = fields.Str(
        required=True, validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if Location.query.filter(
            Location.name.ilike(value),
            Location.domain_id == current_user.domain_id
            ).first():
            raise ValidationError(f"Location name '{value}' already exists.")


class UpdateLocSchema(ma.Schema):
    name = fields.Str(validate=validate.Length(min=1, max=120))
    address = fields.Str(validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if value:
            if Location.query.filter(
                Location.name.ilike(value),
                Location.domain_id == current_user.domain_id).first():
                raise ValidationError(
                    f"Location name '{value}' already exists.")
