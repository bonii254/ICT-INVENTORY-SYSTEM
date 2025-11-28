from marshmallow import (Schema, fields, validates_schema, ValidationError, 
                         pre_load, validate)


class BaseProviderSchema(Schema):
    """Base schema containing shared provider fields."""

    contact_person = fields.Str(
        required=False,
        validate=validate.Length(max=255),
        metadata={"description": "Name of the contact person"}
    )
    email = fields.Email(
        required=False,
        allow_none=True,
        metadata={"description": "Email address of the provider"}
    )
    phone = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        metadata={"description": "Phone number of the provider"}
    )
    address = fields.Str(
        required=False,
        validate=validate.Length(max=255),
        metadata={"description": "Physical or postal address of the provider"}
    )
    provider_type = fields.Str(
        required=False,
        validate=validate.OneOf(["COMPANY", "INDIVIDUAL"]),
        metadata={"description": "Type of provider (COMPANY or INDIVIDUAL)"}
    )

    @pre_load
    def strip_strings(self, data, **kwargs):
        """Trim whitespace from string fields before validation."""
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        return data


class ProviderCreateSchema(BaseProviderSchema):
    """Schema for creating a new provider."""
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=255, 
                            error="Name must be between 2 and 255 characters.")
        ],
        metadata={"description": "Name of the provider (must be unique)."}
    )

    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        """Ensure that mandatory fields are provided for creation."""
        if not data.get("name"):
            raise ValidationError(
                "Provider name is required.", field_name="name")


class ProviderUpdateSchema(BaseProviderSchema):
    """Schema for updating an existing provider."""
    pass
