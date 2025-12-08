from marshmallow import (Schema, fields, validate, validates, ValidationError, 
                         pre_load)
from datetime import date
from app.extensions import ma


class BaseExternalMaintenanceSchema(ma.Schema):
    """Base schema with shared field definitions for maintenance records."""
    
    asset_id = fields.Int(required=True)
    parent_asset_id = fields.Int(allow_none=True)
    provider_id = fields.Int(allow_none=True)

    maintenance_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["REPAIR", "REFURBISH", "CALIBRATION", "UPGRADE", "OTHER"]),
        description="Type of external maintenance work"
    )
    description = fields.Str(
        allow_none=True, validate=validate.Length(max=500))
    Condition_After_Maintenance = fields.Str(
        allow_none=True, validate=validate.Length(max=500))

    expected_return_date = fields.Date(allow_none=True)
    actual_return_date = fields.Date(allow_none=True)

    cost_estimate = fields.Float(allow_none=True)
    actual_cost = fields.Float(allow_none=True)

    status = fields.Str(
        validate=validate.OneOf(
            ["SENT", "IN_PROGRESS", "RETURNED", "CANCELLED"]
        ),
        missing="SENT",
        description="Current maintenance status"
    )
    collected_by = fields.Str(
        allow_none=True, validate=validate.Length(max=255))
    received_by = fields.Str(
        allow_none=True, validate=validate.Length(max=255))

    @pre_load
    def strip_strings(self, data, **kwargs):
        """Trim whitespace from string fields."""
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        return data

    @validates("expected_return_date")
    def validate_expected_date(self, value):
        """Ensure expected date is not before today."""
        if value and value < date.today():
            raise ValidationError(
                "Expected return date cannot be in the past.")


class ExternalMaintenanceCreateSchema(BaseExternalMaintenanceSchema):
    """Schema for creating a maintenance record."""
    pass


class ExternalMaintenanceUpdateSchema(BaseExternalMaintenanceSchema):
    """Schema for updating an existing maintenance record."""
    receipt_number = fields.Str(
        validate=validate.Length(min=3, max=50), required=False)
    asset_id = fields.Int(required=False)
    maintenance_type = fields.Str(required=False)
