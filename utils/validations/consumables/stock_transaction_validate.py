from marshmallow import fields, validate, validates, ValidationError
from app.extensions import ma
from app.models.v1 import Consumables, StockTransaction, Alert

class StockTransactionSchema(ma.Schema):
    consumable_id = fields.Int(required=True)
    department_id = fields.Int(required=True)
    transaction_type = fields.String(
        validate=validate.OneOf(
            ["IN", "OUT"],
            error=(
                "The 'status' must be one of: 'IN' or 'OUT' "
            )))
    quantity = fields.Integer(
        required=False,
        validate=lambda x: x >= 0 if x is not None else True,
        error_messages={
            "invalid": "Quantity level must be a non-negative integer."
        })
