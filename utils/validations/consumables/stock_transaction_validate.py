from marshmallow import fields, validate, validates, ValidationError # type: ignore
from app.extensions import ma
from app.models.v1 import Consumables, StockTransaction, Alert

class StockTransactionSchema(ma.Schema):
    consumable_id = fields.Int(required=True)
    department_id = fields.Int(required=True)
    quantity = fields.Integer(required=False)
    transaction_type = fields.String(
        validate=validate.OneOf(
            ["IN", "OUT"],
            error=(
                "The 'status' must be one of: 'IN' or 'OUT' "
            )))

    @validates("quantity")
    def validate_non_negative(self, value):
        """Ensure quantity is a non-negative integer."""
        if value is not None and value < 0:
            raise ValidationError(
                "Quantity level must be a non-negative integer.")
