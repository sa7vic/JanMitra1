from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.database import db, User
from datetime import timedelta
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    name = data.get('name')
    role = data.get('role', 'citizen')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(
        email=email,
        phone=phone,
        name=name,
        role=role,
        profile_completed=False,
        onboarding_step=0
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30)
    )
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'token': access_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30)
    )
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': access_token
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict())

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    if 'name' in data:
        user.name = data['name']
    if 'city' in data:
        user.city = data['city']
    if 'state' in data:
        user.state = data['state']
    if 'pincode' in data:
        user.pincode = data['pincode']
    if 'location' in data:
        user.location = data['location']
    if 'occupation' in data:
        user.occupation = data['occupation']
    if 'annual_income' in data:
        user.annual_income = data['annual_income']
    if 'family_size' in data:
        user.family_size = data['family_size']
    if 'age' in data:
        user.age = data['age']
    if 'gender' in data:
        user.gender = data['gender']
    if 'education' in data:
        user.education = data['education']
    if 'land_ownership' in data:
        user.land_ownership = data['land_ownership']
    if 'has_ration_card' in data:
        user.has_ration_card = data['has_ration_card']
    if 'profile_completed' in data:
        user.profile_completed = data['profile_completed']
    if 'onboarding_step' in data:
        user.onboarding_step = data['onboarding_step']
    if 'phone' in data:
        user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated',
        'user': user.to_dict()
    })