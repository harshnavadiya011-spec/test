from marshmallow import Schema, fields, validate, validates, ValidationError

class DataSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=30),
        error_messages={
            "required": "Name is required.",
            "invalid": "Invalid name format."
        }
    )
    age = fields.Integer(
        required=True,
        validate=validate.Range(min=0, max=120),
        error_messages={
            "required": "Age is required.",
            "invalid": "Age must be a number."
        }
    )

    @validates("name")
    def validate_name_length(self, value, **kwargs):
        """Custom validation to enforce length between 2 and 30"""
        if len(value.strip()) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        elif len(value.strip()) > 30:
            raise ValidationError("Name cannot exceed 30 characters.")
