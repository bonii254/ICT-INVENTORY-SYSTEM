from marshmallow import fields, validate, validates, ValidationError
from app.extensions import ma, db
from app.models.v1 import Location, User
from flask_jwt_extended import get_jwt_identity


class RegLocSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    address = fields.Str(required=True, validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        user_id = get_jwt_identity()
        if not user_id:
            raise ValidationError("Unable to determine current user.")

        current_user = db.session.get(User, user_id)

        if Location.query.filter(
            Location.name.ilike(value),
            Location.domain_id == current_user.domain_id
        ).first():
            raise ValidationError(f"Location name '{value}' already exists in your domain.")


class UpdateLocSchema(ma.Schema):
    name = fields.Str(validate=validate.Length(min=1, max=120))
    address = fields.Str(validate=validate.Length(min=1, max=120))

    @validates("name")
    def validate_name(self, value):
        if not value:
            return  

        user_id = get_jwt_identity()
        if not user_id:
            raise ValidationError("Unable to determine current user.")

        current_user = db.session.get(User, user_id)

        location_id = self.context.get("location_id")

        exists = Location.query.filter(
            Location.name.ilike(value),
            Location.domain_id == current_user.domain_id,
            Location.id != location_id 
        ).first()

        if exists:
            raise ValidationError(
                f"Location name '{value}' already exists in your domain."
            )