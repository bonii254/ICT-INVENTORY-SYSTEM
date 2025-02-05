from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
import re
from app.models.v1 import Category, User, Location, Status, Department, Asset


class RegAssetSchema(Schema):
    """
    Marshmallow schema for validating Asset creation data.
    """
    ip_address = fields.Str(
        required=False,
        validate=validate.Length(min=7, max=45),
        error_messages={"required": "The 'ip_address' fields is required."}
    )
    mac_address = fields.Str(
        required=False,
        validate=validate.Length(min=12, max=17),
        allow_none=True
    )
    category_id = fields.Int(required=False, allow_none=True)
    assigned_to = fields.Int(required=False, allow_none=True)
    location_id = fields.Int(required=False, allow_none=True)
    status_id = fields.Int(required=False, allow_none=True)
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
    department_id = fields.Int(
        required=False,
        allow_none=True
    )

    @validates("ip_address")
    def validate_ip_address(self, value):
        """
        Validate that the IP address is correctly formatted and unique.
        """
        ipv4_pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

        ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"

        if value:
            if not re.match(ipv4_pattern, value):
                if not re.match(ipv6_pattern, value):
                    raise ValidationError(
                        f"The IP address '{value}' is not valid.")

            if Asset.query.filter_by(ip_address=value).first():
                raise ValidationError(
                    f"The IP address '{value}' is already in use.")

    @validates("mac_address")
    def validate_mac_address(self, value):
        """
        Validate that the MAC address is correctly formatted and unique.
        """
        if value:
            mac_pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
            if not re.match(mac_pattern, value):
                raise ValidationError(
                    f"The MAC address '{value}' is not valid.")
            if Asset.query.filter_by(mac_address=value).first():
                raise ValidationError(
                    f"The MAC address '{value}' is already in use.")

    @validates("category_id")
    def validate_category_id(self, value):
        """
        Ensure the category_id exists in the database.
        """
        if value and not Category.query.get(value):
            raise ValidationError(f"Category with id {value} does not exist.")

    @validates("assigned_to")
    def validate_assigned_to(self, value):
        """
        Ensure the assigned_to user exists in the database.
        """
        if value and not User.query.get(value):
            raise ValidationError(f"User with id {value} does not exist.")

    @validates("location_id")
    def validate_location_id(self, value):
        """
        Ensure the location_id exists in the database.
        """
        if value and not Location.query.get(value):
            raise ValidationError(f"Location with id {value} does not exist.")

    @validates("status_id")
    def validate_status_id(self, value):
        """
        Ensure the status_id exists in the database.
        """
        if value and not Status.query.get(value):
            raise ValidationError(f"Status with id {value} does not exist.")

    @validates("department_id")
    def validate_department_id(self, value):
        """
        Ensure the department_id exists in the database.
        """
        if value and not Department.query.get(value):
            raise ValidationError(
                f"Department with id {value} does not exist."
            )

    @validates("purchase_date")
    def validate_purchase_date(self, value):
        """
        Ensure the purchase_date is not in the future.
        """
        if value and value > datetime.utcnow().date():
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
