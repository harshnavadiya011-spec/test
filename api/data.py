from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.data import Data
from schema.data import DataSchema

bp = Blueprint("api", __name__)
data_schema = DataSchema()

@bp.route("/data", methods=["GET"])
@jwt_required()
def get_data():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 5))
    except ValueError:
        return jsonify({"error": "Page number must be an integer"}), 400

    search = request.args.get("search", "").strip()
    query = Data.query

    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Data.name.ilike(f"%{search}%"),
                Data.age.cast(db.String).like(f"%{search}%")
            )
        )

    query = query.order_by(Data.id.asc())
    data = query.paginate(page=page, per_page=per_page, error_out=False)

    result = {
        "page": data.page,
        "per_page": data.per_page,
        "total_item": data.total,
        "total_page": data.pages,
        "data": [
            {
                "id": d.id,
                "name": d.name,
                "age": d.age
            } for d in data.items
        ]
    }
    return jsonify(result), 200




@bp.route("/data/<int:id>", methods=["GET"])
@jwt_required()
def get(id):
    data = Data.query.get(id)
    if not data:
        return jsonify({"error": f"Data {id} you need not found"}), 404
    
    return jsonify({
                     "id": data.id,
                     "name": data.name,
                     "age": data.age
                    }), 200


@bp.route("/data", methods=["POST"])
@jwt_required()
def add_data():
    
    data = request.get_json() if request.is_json else request.form.to_dict()

    errors = data_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    new_record = Data(
        name=data["name"],
        age=int(data["age"])
    )

    db.session.add(new_record)
    db.session.commit()

    return jsonify({
        "message": f"Data {new_record} added successfully"
    }), 201



@bp.route("/data/<int:id>", methods=["PUT"])
@jwt_required()
def update_data(id):
    record = Data.query.get(id)

    if not record:
        return jsonify({"error": f"Data {id} you need to Update not found"}), 404
    
    data = request.form.to_dict() or request.get_json()
    record.name = data.get("name", record.name)
    record.age = data.get("age", record.age)
    db.session.commit()
    return jsonify({"message": f"Data {id} updated successfully"}), 200



@bp.route("/data/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_data(id):
    data = Data.query.get(id)

    if not data:
        return jsonify({"error": f"Data {id} you need to Delete, not found"}), 404
    
    db.session.delete(data)
    db.session.commit()
    return jsonify({"message": f"Data {id} deleted successfully"}), 200



@bp.route("/data/export", methods=["GET"])
@jwt_required()
def export_data():
    search = request.args.get("search", "").strip()
    query = Data.query

    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Data.name.ilike(f"%{search}%"),
                Data.age.cast(db.String).like(f"%{search}%")
            )
        )

    query = query.order_by(Data.id.asc())
    data = query.all()

    result = [
        {"id": d.id, "name": d.name, "age": d.age}
        for d in data
    ]
    return jsonify(result), 200






















































