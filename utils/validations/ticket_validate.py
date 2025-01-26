from marshmallow import fields, validate, validates, ValidationError, post_load
from app.models.v1 import Asset, User
from app.extensions import ma


class RegTicSchema(ma.Schema):
    """
    Schema for validating schema creation
    """
    asset_id = fields.Int(
        required=True,
        error_messages={"required": "The 'asset_id' field is required."}
    )
    user_id = fields.Int(
        required=True,
        error_messages={"required": "The 'user_id' field is required."}
    )
    status = fields.String(
        required=True,
        validate=validate.OneOf(
            ["Open", "In Progress", "Closed"],
            error=(
                "The 'status' must be one of: 'Open', "
                "'In Progress', or 'Closed'."
            )
        ),
        error_messages={"required": "The 'status' field is required."}
    )
    description = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )
    resolution_notes = fields.Str(
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

    @validates("user_id")
    def validate_user_id(self, value):
        """
        Ensure the user_id exists in the database.
        """
        if not User.query.get(value):
            raise ValidationError(f"User with id {value} does not exist.")


class UpdateTicSchema(ma.Schema):
    asset_id = fields.Int()
    user_id = fields.Int()
    status = fields.String(
        validate=validate.OneOf(
            ["Open", "In Progress", "Closed"],
            error=(
                "The 'status' must be one of: 'Open', "
                "'In Progress', or 'Closed'."
            )
        ),
    )
    description = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )
    resolution_notes = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )

    @validates("asset_id")
    def validate_asset_id(self, value):
        """
        Ensure the asset_id exists in the database.
        """
        if value:
            if not Asset.query.get(value):
                raise ValidationError(f"Asset with id {value} does not exist.")

    @validates("user_id")
    def validate_user_id(self, value):
        """
        Ensure the user_id exists in the database.
        """
        if value:
            if not User.query.get(value):
                raise ValidationError(f"User with id {value} does not exist.")
