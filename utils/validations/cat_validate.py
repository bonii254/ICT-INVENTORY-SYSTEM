from marshmallow import (
    fields, post_load, validate, validates, ValidationError)
from app.extensions import ma
from app.models.v1 import Category


class RegCatSchema(ma.Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    description = fields.Str(required=True)

    @validates("name")
    def validate_name(self, value):
        if Category.query.filter(Category.name.ilike(value)).first():
            raise ValidationError(f"Category name '{value}' already exists.")

    @post_load
    def process_Category(self, data, **kwargs):
        data['name'] = data['name'].capitalize()
        return Category(**data)
