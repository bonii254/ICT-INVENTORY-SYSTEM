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

    @validates('name')
    def validate_name(self, value):
        """Ensure name is unique"""
        if Consumables.query.filter_by(name=value).first():
            raise ValidationError(f"Consumable name '{value}' already exist.")


class UpdateConSchema(ma.Schema):
    """
    Schema for validating consumable update
    """
    name = fields.String()
    category = fields.String()
    brand = fields.String()
    model = fields.String()
    unit_of_measure = fields.String()
    reorder_level = fields.Integer(
        validate=lambda x: x >= 0,
        error_messages={"invalid":
                        "Reorder level must be a non-negative integer."}
    )

    @validates('name')
    def validate_name(self, value):
        """Ensure name is unique"""
        if value:
            if Consumables.query.filter_by(name=value).first():
                raise ValidationError(
                    f"Consumable name '{value}' already exist.")
