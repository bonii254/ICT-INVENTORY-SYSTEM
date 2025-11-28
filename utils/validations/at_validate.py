from marshmallow import fields, validates, ValidationError, validates_schema 
from app.extensions import ma, db
from app.models.v1 import Asset, Location, User


class RegATSchema(ma.Schema):
    """
    Marshmallow schema for validating AssetTransfer data.
    """

    asset_id = fields.Integer(required=True)
    to_location_id = fields.Integer(required=True)
    transferred_to = fields.Integer(required=True)
    notes = fields.String(required=True)

    """
    @validates("asset_id")
    def validate_asset_id(self, value):
        Validate that the asset exists.
        if not db.session.get(Asset, value):
            raise ValidationError(f"Asset with id {value} does not exist.")
    """

    @validates("to_location_id")
    def validate_to_location_id(self, value):
        """Validate that the to_location exists."""
        if not db.session.get(Location, value):
            raise ValidationError(f"Location with id {value} does not exist.")

    @validates("transferred_to")
    def validate_transferred_to(self, value):
        """
        Validate that the user receiving the transfer exists and
        ensure no self-transfer.
        """
        user = db.session.get(User, value)
        if not user:
            raise ValidationError(f"User with id {value} does not exist.")

        asset_id = self.context.get("asset_id")
        if asset_id:
            asset = db.session.get(Asset, asset_id)

            if asset and asset.assigned_to == value:
                raise ValidationError(
                    "An asset cannot be transferred to the same user.")

    def validate(self, data, **kwargs):
        """
        Custom validation to inject context for transferred_from and
        asset_id.
        """
        self.context["transferred_from"] = data.get("transferred_from")
        self.context["asset_id"] = data.get("asset_id")
        super().validate(data, **kwargs)


class UpdateATSchema(ma.Schema):
    asset_id = fields.Integer()
    to_location_id = fields.Integer()
    transferred_to = fields.Integer()
    notes = fields.String()


    @validates("asset_id")
    def validate_asset_id(self, value):
        """Validate that the asset exists."""
        if value:
            if not db.session.get(Asset, value):
                raise ValidationError(f"Asset with id {value} does not exist.")

    @validates("to_location_id")
    def validate_to_location_id(self, value):
        """Validate that the to_location exists."""
        if value:
            if not isinstance(value, int):
                raise ValidationError("to_location_id must be an integer.")
            if not db.session.get(Location, value):
                raise ValidationError(
                    f"Location with id {value} does not exist.")


    @validates("transferred_to")
    def validate_transferred_to(self, value):
        """
        Validate that the user receiving the transfer exists and
        ensure no self-transfer.
        """
        if value:
            if not isinstance(value, int):
                raise ValidationError("transferred_to must be an integer.")
            user = db.session.get(User, value)
            if not user:
                raise ValidationError(f"User with id {value} does not exist.")

            asset_id = self.context.get("asset_id")
            if asset_id:
                asset = db.session.get(Asset, asset_id)

            if asset and asset.assigned_to == value:
                raise ValidationError(
                    "An asset cannot be transferred to the same user.")

    @validates_schema
    def validate(self, data, **kwargs):
        """
        Custom validation to inject context for transferred_from and
        asset_id.
        """
        self.context["asset_id"] = data.get("asset_id")
        super().validate(data, **kwargs)
