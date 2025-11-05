from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extensions import db
from models.user import User
from schema.auth import UserSchema, LoginSchema,Reset
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

user_schema = UserSchema()
login_schema = LoginSchema()
reset = Reset()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() if request.is_json else request.form.to_dict()

    errors = user_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password, phone=phone)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201



@auth_bp.route("/register", methods=["GET"])
def get_users():
    users = User.query.all()
    result = [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "phone": u.phone
        } for u in users]
    return jsonify(result), 200



@auth_bp.route("/register/<int:id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": f"User {id} not found"}), 400
    
    return jsonify({
                     "id" : user.id,
                     "name" : user.name,
                     "email" : user.email,
                     "phone" : user.phone
                   }), 200



@auth_bp.route("/register/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": f"Data {id} you need to Delete, not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Data {id} deleted successfully"}), 200



@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() if request.is_json else request.form.to_dict()
    errors = login_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30)
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200





@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() if request.is_json else request.form.to_dict()

    error = reset.validate(data)
    if error:
        return jsonify({"error" : error})
    
    email = data.get("email")
    new_password = data.get("new_password") 

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email does not exist"}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200
