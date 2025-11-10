from marshmallow import Schema, fields, validate, validates, ValidationError
from models.service import Service
from sqlalchemy import func

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class ServiceSchema(Schema):
    service = fields.String(
        required=True,
        validate=validate.Length(min=5, max=200),
        error_messages={
            "required": "Enter user-friendly service name.",
            "invalid": "Invalid service format."
        }
    )

    price = fields.Float(
        required=True,
        validate=validate.Range(min=100, max=5000),
        error_messages={
            "required": "Please enter your service charge.",
            "invalid": "Your charge is out of our allowed range."
        }
    )

    image = fields.String(required=False)

    def __init__(self, current_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_id = current_id

    @validates("service")
    def validate_service_unique(self, value, **kwargs):
        # Normalize case
        existing = Service.query.filter(func.lower(Service.service) == func.lower(value)).first()
        # Only raise if a different service with the same name exists
        if existing and (self.current_id is None or existing.id != self.current_id):
            raise ValidationError(f"Service '{value}' already exists.")

    @validates("image")
    def validate_image_extension(self, value, **kwargs):
        if value and not allowed_file(value):
            raise ValidationError("Invalid image format. Allowed: png, jpg, jpeg, gif.")
