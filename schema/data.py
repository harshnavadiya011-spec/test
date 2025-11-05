from marshmallow import Schema, fields, validate

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
