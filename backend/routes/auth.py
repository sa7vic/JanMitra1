from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from models.database import User, db
from utils.locations import is_valid_city, is_valid_district, is_valid_state

auth_bp = Blueprint('auth', __name__)


def normalize_role(role: str | None) -> str:
    """Normalize incoming role values to canonical backend roles."""
    normalized = (role or 'citizen').strip().lower()
    if normalized == 'gov':
        return 'government'
    if normalized in {'citizen', 'government', 'admin'}:
        return normalized
    return 'citizen'


def _clean_str(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


GENERIC_EMAIL_DOMAINS = {
    'gmail.com',
    'yahoo.com',
    'hotmail.com',
    'outlook.com',
    'live.com',
    'icloud.com',
    'aol.com',
    'proton.me',
    'protonmail.com',
}


def validate_location_for_role(role: str, gov_level: str | None, state: str | None, district: str | None, city: str | None):
    if role == 'citizen':
        if not state or not district or not city:
            raise ValueError('state, district, and city are required for citizen registration')
        if not is_valid_state(state):
            raise ValueError('Invalid state selection')
        if not is_valid_district(state, district):
            raise ValueError('Invalid district for selected state')
        if not is_valid_city(state, district, city):
            raise ValueError('Invalid city for selected district')
        return

    if role != 'government':
        return

    if gov_level == 'national':
        return

    if gov_level in {'state', 'district', 'local'} and not state:
        raise ValueError('state is required for selected government level')
    if state and not is_valid_state(state):
        raise ValueError('Invalid state selection')

    if gov_level in {'district', 'local'} and not district:
        raise ValueError('district is required for selected government level')
    if district and not is_valid_district(state, district):
        raise ValueError('Invalid district for selected state')

    if gov_level == 'local' and not city:
        raise ValueError('city is required for local government level')
    if city and not is_valid_city(state, district, city):
        raise ValueError('Invalid city for selected district')


def validate_official_email(email: str):
    if '@' not in email:
        raise ValueError('Invalid official email format')
    domain = email.rsplit('@', 1)[1].lower()
    if domain in GENERIC_EMAIL_DOMAINS:
        raise ValueError('Government users must use an official organization email domain')


def validate_government_payload(role: str, data: dict):
    gov_level = _clean_str(data.get('gov_level'))
    if gov_level:
        gov_level = gov_level.lower()

    state = _clean_str(data.get('state'))
    district = _clean_str(data.get('district'))
    city = _clean_str(data.get('city'))

    if role != 'government':
        return {
            'gov_level': None,
            'state': state,
            'district': district,
            'city': city,
            'department': None,
            'designation': None,
            'official_email': None,
        }

    if not gov_level:
        raise ValueError('gov_level is required for government users')

    allowed_levels = {'national', 'state', 'district', 'local'}
    if gov_level not in allowed_levels:
        raise ValueError('Invalid gov_level. Allowed: national, state, district, local')

    if gov_level == 'state' and not state:
        raise ValueError('state is required for state-level government users')
    if gov_level == 'district' and (not state or not district):
        raise ValueError('state and district are required for district-level government users')
    if gov_level == 'local' and (not state or not district or not city):
        raise ValueError('state, district, and city are required for local-level government users')

    department = _clean_str(data.get('department'))
    designation = _clean_str(data.get('designation'))
    official_email = _clean_str(data.get('official_email') or data.get('email'))

    if not department:
        raise ValueError('department is required for government users')
    if not designation:
        raise ValueError('designation is required for government users')
    if not official_email:
        raise ValueError('official_email is required for government users')

    validate_official_email(official_email)

    validate_location_for_role(role, gov_level, state, district, city)

    return {
        'gov_level': gov_level,
        'state': state,
        'district': district,
        'city': city,
        'department': department,
        'designation': designation,
        'official_email': official_email,
    }


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    name = data.get('name')
    role = normalize_role(data.get('role', 'citizen'))

    if role == 'government':
        email = _clean_str(data.get('official_email') or email)
    else:
        email = _clean_str(email)

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    try:
        gov_data = validate_government_payload(role, data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    if role == 'citizen':
        state = _clean_str(data.get('state'))
        district = _clean_str(data.get('district'))
        city = _clean_str(data.get('city'))
        try:
            validate_location_for_role(role, None, state, district, city)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        gov_data['state'] = state
        gov_data['district'] = district
        gov_data['city'] = city

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(
        email=email,
        official_email=gov_data.get('official_email'),
        phone=phone,
        name=name,
        role=role,
        gov_level=gov_data['gov_level'],
        department=gov_data.get('department'),
        designation=gov_data.get('designation'),
        state=gov_data['state'],
        district=gov_data['district'],
        city=gov_data['city'],
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

    # One-way migration for legacy role values.
    if user.role == 'gov':
        user.role = 'government'
        if not user.gov_level:
            user.gov_level = 'national'

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

    if user.role == 'gov':
        user.role = 'government'
        if not user.gov_level:
            user.gov_level = 'national'
        db.session.commit()

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
    if 'department' in data:
        user.department = data['department']
    if 'designation' in data:
        user.designation = data['designation']

    db.session.commit()

    return jsonify({
        'message': 'Profile updated',
        'user': user.to_dict()
    })
