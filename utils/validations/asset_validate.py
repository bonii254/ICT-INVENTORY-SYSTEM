from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime, timezone
import re
from app.extensions import db
from app.models.v1 import (Category, User, Location, Status, Department, Asset,
                           Domain)


class RegAssetSchema(Schema):
    """
    Marshmallow schema for validating Asset creation data.
    """
    model_number = fields.Str(
        required=False
    )
    serial_number = fields.Str(
        required=False
    )
    fresha_tag = fields.Str(required=False)
    category_id = fields.Int(required=True)
    assigned_to = fields.Int(required=True)
    location_id = fields.Int(required=True)
    status_id = fields.Int(required=True)
    department_id = fields.Int(required=True)
    purchase_date = fields.Date(
        required=False,
        allow_none=True,
        error_messages={
            "invalid": "The 'purchase_date' must be in YYYY-MM-DD format."}
    )
    warranty_expiry = fields.Date(
        required=False,
        allow_none=True,
        error_messages={
            "invalid": "The 'warranty_expiry' must be in YYYY-MM-DD format."}
    )
    configuration = fields.Str(
        required=False,
        allow_none=True,
        validate=fields.Length(max=1000),
        error_messages={
            "invalid": "The 'configuration' field must be a valid string.",
            "max_length":
            "The 'configuration' field cannot exceed 1000 characters."
        }
    )

    @validates("category_id")
    def validate_category_id(self, value):
        """
        Ensure the category_id exists in the database.
        """
        if value and not db.session.get(Category, value):
            raise ValidationError(f"Category with id {value} does not exist.")

    @validates("assigned_to")
    def validate_assigned_to(self, value):
        """
        Ensure the assigned_to user exists in the database.
        """
        if value and not db.session.get(User, value):
            raise ValidationError(f"User with id {value} does not exist.")

    @validates("location_id")
    def validate_location_id(self, value):
        """
        Ensure the location_id exists in the database.
        """
        if value and not db.session.get(Location, value):
            raise ValidationError(f"Location with id {value} does not exist.")

    @validates("status_id")
    def validate_status_id(self, value):
        """
        Ensure the status_id exists in the database.
        """
        if value and not db.session.get(Status, value):
            raise ValidationError(f"Status with id {value} does not exist.")

    @validates("department_id")
    def validate_department_id(self, value):
        """
        Ensure the department_id exists in the database.
        """
        if value and not db.session.get(Department, value):
            raise ValidationError(
                f"Department with id {value} does not exist."
            )

    @validates("purchase_date")
    def validate_purchase_date(self, value):
        """
        Ensure the purchase_date is not in the future.
        """
        if value and value > datetime.now(timezone.utc).date():
            raise ValidationError(
                "The 'purchase_date' cannot be in the future."
            )

    @validates("warranty_expiry")
    def validate_warranty_expiry(self, value):
        """
        Ensure the warranty_expiry date is not earlier than the purchase_date.
        """
        if value and "purchase_date" in self.context:
            purchase_date = self.context["purchase_date"]
            if purchase_date and value < purchase_date:
                raise ValidationError(
                    "The 'warranty_expiry' cannot be earlier than the\
                          'purchase_date'.")

    @validates("serial_number")
    def validate_serial_number(self, value):
        """
        Ensure the serial_number is unique in the database.
        """
        if value:
            existing = db.session.query(
                Asset).filter_by(serial_number=value).first()
            if existing:
                raise ValidationError(
                    f"Asset with serial number '{value}' already exists.")


class UpdateAssetSchema(Schema):
    """
    Marshmallow schema for validating Asset update data.
    """

    model_number = fields.Str(required=False, allow_none=True)
    serial_number = fields.Str(required=False, allow_none=True)
    fresha_tag = fields.Str(required=False, allow_none=True)
    category_id = fields.Int(required=False, allow_none=True)
    assigned_to = fields.Int(required=False, allow_none=True)
    location_id = fields.Int(required=False, allow_none=True)
    status_id = fields.Int(required=False, allow_none=True)
    department_id = fields.Int(required=False, allow_none=True)
    purchase_date = fields.Date(
        required=False,
        allow_none=True,
        error_messages={
            "invalid": "The 'purchase_date' must be in YYYY-MM-DD format."
        },
    )
    warranty_expiry = fields.Date(
        required=False,
        allow_none=True,
        error_messages={
            "invalid": "The 'warranty_expiry' must be in YYYY-MM-DD format."
        },
    )
    configuration = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000),
        error_messages={
            "invalid": "The 'configuration' field must be a valid string.",
            "max_length":
            "The 'configuration' field cannot exceed 1000 characters.",
        },
    )

    @validates("category_id")
    def validate_category_id(self, value):
        if value and not db.session.get(Category, value):
            raise ValidationError(f"Category with id {value} does not exist.")

    @validates("assigned_to")
    def validate_assigned_to(self, value):
        if value and not db.session.get(User, value):
            raise ValidationError(f"User with id {value} does not exist.")

    @validates("location_id")
    def validate_location_id(self, value):
        if value and not db.session.get(Location, value):
            raise ValidationError(f"Location with id {value} does not exist.")

    @validates("status_id")
    def validate_status_id(self, value):
        if value and not db.session.get(Status, value):
            raise ValidationError(f"Status with id {value} does not exist.")

    
    @validates("department_id")
    def validate_department_id(self, value):
        if value and not db.session.get(Department, value):
            raise ValidationError(
                f"Department with id {value} does not exist.")

    @validates("purchase_date")
    def validate_purchase_date(self, value):
        if value and value > datetime.now(timezone.utc).date():
            raise ValidationError(
                "The 'purchase_date' cannot be in the future.")

    @validates("warranty_expiry")
    def validate_warranty_expiry(self, value):
        if value and "purchase_date" in self.context:
            purchase_date = self.context["purchase_date"]
            if purchase_date and value < purchase_date:
                raise ValidationError(
                    "The 'warranty_expiry' cannot be earlier \
                        than the 'purchase_date'."
                )

    @validates("serial_number")
    def validate_serial_number(self, value):
        """
        Ensure the serial_number is unique, excluding
        the current asset being updated.
        Requires 'asset_id' in context.
        """
        if value:
            query = db.session.query(Asset).filter_by(serial_number=value)
            if "asset_id" in self.context:
                query = query.filter(Asset.id != self.context["asset_id"])
            existing = query.first()
            if existing:
                raise ValidationError(
                    f"Asset with serial number '{value}' already exists."
                )
