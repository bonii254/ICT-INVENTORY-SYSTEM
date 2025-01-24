from marshmallow import fields, validate, validates, ValidationError
from app.extensions import ma
from app.models.v1 import Asset


class RegAlcSchema(ma.Schema):
    asset_id = fields.Int(
        required=True,
        error_messages={"required": "The 'asset_id' field is required."}
    )
    event = fields.String(
        required=True,
        validate=validate.Length(max=255),
        error_messages={"required": "The 'event' field is required."}
    )
    notes = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )

    @validates("asset_id")
    def validate_asset_id(self, value):
        """
        Ensure the asset_id exists in the database.
        """
        if not Asset.query.get(value):
            raise ValidationError(f"Asset with id {value} does not exist.")

    @validates("event")
    def validate_event(self, value):
        """
        Ensure the event field is not empty and properly formatted.
        """
        if not value.strip():
            raise ValidationError("The 'event' field cannot be empty.")
