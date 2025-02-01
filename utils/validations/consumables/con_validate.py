from marshmallow import (
    fields, post_load, validate, validates, ValidationError)
from app.extensions import ma
from app.models.v1 import Consumables


class RegConSchema(ma.Schema):
    """
    Schema for validating consumable registration requests.
    """
    name = fields.String(
        required=True,
        error_messages={"required": "Name is required."})
    category = fields.String(
        required=True,
        error_messages={"required": "Category is required."})
    brand = fields.String(
        required=True,
        error_messages={"required": "Brand is required."})
    model = fields.String()
    unit_of_measure = fields.String(
        required=True,
        error_messages={"required": "Unit of measure is required."})
    reorder_level = fields.Integer(
        required=True,
        validate=lambda x: x >= 0,
        error_messages={"required": "Reorder level is required.", \
                        "invalid":
                        "Reorder level must be a non-negative integer."}
    )


