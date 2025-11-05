from marshmallow import Schema, fields, validate, ValidationError
import re
from models.user import User  

# def validate_password(password):
#     if len(password) < 8:
#         raise ValidationError("Password must be at least 8 characters long.")
#     if len(password) > 32:
#         raise ValidationError("Password must not exceed 32 characters.")
#     if not re.search(r"[A-Z]", password):
#         raise ValidationError("Password must contain at least one uppercase letter.")
#     if not re.search(r"[a-z]", password):
#         raise ValidationError("Password must contain at least one lowercase letter.")
#     if not re.search(r"\d", password):
#         raise ValidationError("Password must contain at least one digit.")
#     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
#         raise ValidationError("Password must contain at least one special character.")
#     if re.search(r"\s", password):
#         raise ValidationError("Password cannot contain spaces.")




def validate_email_format(email):
    """Advanced email format validation."""
    if "@" not in email:
        raise ValidationError("Email must contain '@'.")
    if " " in email:
        raise ValidationError("Email cannot contain spaces.")
    if ".." in email:
        raise ValidationError("Email cannot contain consecutive dots.")
    if not re.search(r"\.[A-Za-z]{2,}$", email):
        raise ValidationError("Email must contain a valid domain extension (e.g., .com, .org).")


def email_must_not_exist(email):
    if User.query.filter_by(email=email).first():
        raise ValidationError("This email is already registered.")


def email_must_exist(email):
    if not User.query.filter_by(email=email).first():
        raise ValidationError("No account found with this email.")

def validate_phone(phone):
    if not re.match(r"^\+?\d{7,15}$", phone):
        raise ValidationError(
            "Phone number must contain only digits"
        )
    
def phone_must_not_exist(phone):
    if User.query.filter_by(phone=phone).first():
        raise ValidationError("This phone is already registered.")



class UserSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={
            "required": "Name is required.",
            "invalid": "Invalid name format."
        }
    )
    email = fields.Email(
        required=True,
        validate=validate.And(
            validate_email_format,
            email_must_not_exist
        ),
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email format."
        }
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=4, max=12),    
        error_messages={
            "required": "Password is required.",
            "invalid": "Invalid password format."
        }
    )
    phone = fields.String(
        required=True,
        validate=validate.And
        (
            validate_phone,
            phone_must_not_exist
        ),
        error_messages={
            "required": "Phone number is required.",
            "invalid": "Invalid phone number format."
        }
    )

class LoginSchema(Schema):

    email = fields.Email(
            required=True,
            validate=validate.And(
                validate_email_format,
                email_must_exist
            ),
            error_messages={
                "required": "Email is required.",
                "invalid": "Invalid email format."
            }
        )
    password = fields.String(
            required=True,
            validate=validate.Length(min=4, max=12),    
            error_messages={
                "required": "Password is required.",
                "invalid": "Invalid password format."
            }
        )
    
class Reset(Schema):
    email = fields.Email(
            required=True,
            validate=validate.And(
                validate_email_format,
                email_must_exist     
            ),
            error_messages={
                "required": "Email is required.",
                "invalid": "Invalid email format."
            }
        )
    new_password = fields.String(
            required=True,
            validate=validate.Length(min=4, max=12),    
            error_messages={
                "required": "Password is required.",
                "invalid": "Invalid password format."
            }
        )
    

