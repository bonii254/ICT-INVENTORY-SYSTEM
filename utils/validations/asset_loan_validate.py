from marshmallow import Schema, fields, validates, ValidationError
from datetime import datetime


class BaseAssetLoanSchema(Schema):
    asset_id = fields.Int(required=True)
    borrower_id = fields.Int(required=True)
    expected_return_date = fields.Date(required=True)
    condition_before = fields.Str(required=True)
    remarks = fields.Str(allow_none=True)
    status = fields.Str(
        validate=lambda s: s in ['BORROWED', 'RETURNED', 'OVERDUE'],
        dump_default='BORROWED'
    )


class AssetLoanCreateSchema(BaseAssetLoanSchema):
    """Schema for creating a new asset loan."""

    @validates("expected_return_date")
    def validate_expected_return_date(self, value):
        if value < datetime.today().date():
            raise ValidationError(
                "Expected return date cannot be in the past.")


class AssetLoanUpdateSchema(Schema):
    """Schema for updating an existing asset loan."""
    actual_return_date = fields.DateTime(allow_none=True)
    condition_after = fields.Str(allow_none=True)
    remarks = fields.Str(allow_none=True)
    status = fields.Str(
        validate=lambda s: s in ['BORROWED', 'RETURNED', 'OVERDUE'])
