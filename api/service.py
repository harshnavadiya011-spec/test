import os, uuid
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from marshmallow import ValidationError
from extensions import db
from models.service import Service
from schema.service import ServiceSchema

service_bp = Blueprint("service", __name__)
service_schema = ServiceSchema()

UPLOAD_FOLDER = "uploads/services"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE_MB = 2
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS




@service_bp.route("/uploads/services/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)




@service_bp.route("/service", methods=["POST"])
@jwt_required()
def add_service():
    data = request.get_json() if request.is_json else request.form.to_dict()

    try:
        validated_data = service_schema.load(data)
    except ValidationError as err:
        return jsonify({"status": "error", "errors": err.messages}), 400

    image_file = request.files.get("image")
    image_filename = None

    if image_file:
        if not allowed_file(image_file.filename):
            return jsonify({"status": "error", "message": "Invalid image format"}), 400
        image_file.seek(0, os.SEEK_END)
        size_mb = image_file.tell() / (1024 * 1024)
        image_file.seek(0)
        if size_mb > MAX_FILE_SIZE_MB:
            return jsonify({"status": "error", "message": f"Max {MAX_FILE_SIZE_MB}MB allowed"}), 400

        ext = image_file.filename.rsplit(".", 1)[1].lower()
        image_filename = f"{uuid.uuid4().hex}.{ext}"
        image_file.save(os.path.join(UPLOAD_FOLDER, image_filename))

    new_service = Service(
        service=validated_data["service"],
        price=validated_data["price"],
        image=image_filename
    )

    db.session.add(new_service)
    db.session.commit()

    image_url = f"/uploads/services/{image_filename}" if image_filename else None

    return jsonify({
        "status": "success",
        "service": {
            "id": new_service.id,
            "service": new_service.service,
            "price": new_service.price,
            "image": image_url,
            "created_at": new_service.created_at
        }
    }), 201





@service_bp.route("/service", methods=["GET"])
@jwt_required()
def get_service():
    service = Service.query.order_by(Service.id.asc()).all()
    result =  [
           {
            "id" : s.id,
            "image" : s.image,
            "service" : s.service,
            "price" :s.price,
            "created_at" : s.created_at,
            "updated_at" : s.updated_at
    } for s in service]
    return jsonify(result),200





@service_bp.route("/service/<int:id>", methods=["GET"])
@jwt_required()
def getsingle_service(id):
    service = Service.query.get(id)

    if not service:
        return jsonify({"error" : f"Service {id} not found"})
    
    return jsonify({ 
            "id" : service.id,
            "image" : service.image,
            "service" : service.service,
            "price" :service.price,
            "created_at" : service.created_at,
            "updated_at" : service.updated_at
            }),200





@service_bp.route("/service/<int:id>", methods=["PUT"])
@jwt_required()
def update_service(id):
    service = Service.query.get(id)
    if not service:
        return jsonify({"error": f"Service {id} not found"}), 404

    data = request.form.to_dict()
    image_file = request.files.get("image")
    service_schema = ServiceSchema(current_id=id)

    try:
        validated_data = service_schema.load(data)
    except ValidationError as err:
        return jsonify({"status": "error", "errors": err.messages}), 400

    service.service = validated_data.get("service", service.service)
    service.price = validated_data.get("price", service.price)

    if image_file:
        if not allowed_file(image_file.filename):
            return jsonify({"status": "error", "message": "Invalid image format"}), 400
        ext = image_file.filename.rsplit(".", 1)[1].lower()
        image_filename = f"{uuid.uuid4().hex}.{ext}"
        image_file.save(os.path.join(UPLOAD_FOLDER, image_filename))
        service.image = image_filename

    db.session.commit()

    return jsonify({
        "status": "success",
        "service": {
            "id": service.id,
            "service": service.service,
            "price": service.price,
            "image": f"/uploads/services/{service.image}" if service.image else None
        }
    }), 200





@service_bp.route("/service/<int:id>", methods=["DELETE"])
@jwt_required()
def del_service(id):
    service = Service.query.get(id)

    if not service:
        return jsonify({"error" : f"Service {id} not found"})
    
    db.session.delete(service)
    db.session.commit()

    return jsonify({
        "status" : "success",
        "message" : "Service deleted successfully",
        "service" : {
            "id" : service.id,
            "service" :service.service,
            "image" :service.image,
            "price" :service.price,
            "created_at" :service.created_at,
            "updated_at" :service.updated_at
        }
        })

