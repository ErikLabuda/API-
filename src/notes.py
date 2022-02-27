from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Note, db
from flasgger import swag_from

notes = Blueprint("notes", __name__, url_prefix="/api/notes")


@notes.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_notes():
    current_user = get_jwt_identity()

    if request.method == 'POST':

        body = request.get_json().get('body', '')
      
        if Note.query.filter_by(body=body).first():
            return jsonify({
                'error': 'Táto poznámka už existuje'
            }), HTTP_409_CONFLICT

        note = Note(body=body, user_id=current_user)
        db.session.add(note)
        db.session.commit()

        return jsonify({
            'id': note.id,
            'body': note.body,
            'created_at': note.created_at,
            'updated_at': note.updated_at,
        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        notes = Note.query.filter_by(
            user_id=current_user).paginate(page=page, per_page=per_page)

        data = []

        for note in notes.items:
            data.append({
                'id': note.id,
                'body': note.body,
                'created_at': note.created_at,
                'updated_at': note.updated_at,
            })

       
        return jsonify({'data': data}), HTTP_200_OK


@notes.get("/<int:id>")
@jwt_required()
def get_note(id):
    current_user = get_jwt_identity()

    note = Note.query.filter_by(user_id=current_user, id=id).first()

    if not note:
        return jsonify({'message': 'Položka nenájdená'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': note.id,
        'body': note.body,
        'created_at': note.created_at,
        'updated_at': note.updated_at,
    }), HTTP_200_OK


@notes.delete("/<int:id>")
@jwt_required()
def delete_note(id):
    current_user = get_jwt_identity()

    note = Note.query.filter_by(user_id=current_user, id=id).first()

    if not note:
        return jsonify({'message': 'Položka nenájdená'}), HTTP_404_NOT_FOUND

    db.session.delete(note)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@notes.put('/<int:id>')
@notes.patch('/<int:id>')
@jwt_required()
def editnote(id):
    current_user = get_jwt_identity()

    note = Note.query.filter_by(user_id=current_user, id=id).first()

    if not note:
        return jsonify({'message': 'Polozka nenajdena'}), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
     
    note.body = body

    db.session.commit()

    return jsonify({
        'id': note.id,
        'body': note.body,
        'created_at': note.created_at,
        'updated_at': note.updated_at,
    }), HTTP_200_OK


@notes.get("/stats")
@jwt_required()
@swag_from("./docs/notes/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Note.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'body': item.body,
            'id': item.id,
            
        }

        data.append(new_link)

    return jsonify({'data': data}), HTTP_200_OK
