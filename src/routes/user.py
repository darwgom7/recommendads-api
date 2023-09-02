from src.models.models import db, Ad, User, UserInteraction
from flask import Flask, Blueprint, jsonify, request

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
import logging

user = Blueprint('user_blueprint', __name__)
@user.route('login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):

            access_token = create_access_token(identity=user.id, additional_claims={"username": user.username, "role": user.role})
            return jsonify({"access_token": access_token}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        print('Error: ', e)
        return jsonify({"error": str(e)}), 500
    
@user.route('', methods=['GET'])
def get_users():
    try:
        logging.getLogger('flask_cors').level = logging.DEBUG
        users = User.query.all()
        users_data = []

        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
            users_data.append(user_data)

        return jsonify(users_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user.route('read/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }

        return jsonify(user_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user.route('create', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'interactor')
        new_user = User(username=username, password=password, role=role)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user.route('update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        username = data.get('username')
        role = data.get('role')

        user.username = username
        user.role = role

        db.session.commit()

        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user.route('delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route('auth', methods=['GET'])
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user:
        user_data = {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
        return jsonify(user_data), 200
    else:
        return jsonify({"error": "User not found"}), 404