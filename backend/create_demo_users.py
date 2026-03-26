from app import app
from models.database import db, User
from datetime import datetime

with app.app_context():
    users_data = [
        {
            'email': 'ramesh@janmitra.in',
            'password': 'citizen123',
            'name': 'Ramesh Kumar',
            'role': 'citizen',
            'phone': '+919876543210',
            'city': 'Ludhiana',
            'state': 'Punjab',
            'pincode': '141001',
            'occupation': 'Farmer',
            'annual_income': 300000,
            'family_size': 4,
            'age': 42,
            'gender': 'male',
            'education': 'Secondary (9-10)',
            'land_ownership': True,
            'has_ration_card': True,
            'profile_completed': True,
            'location': 'Ludhiana, Punjab'
        },
        {
            'email': 'priya@janmitra.in',
            'password': 'citizen123',
            'name': 'Priya Sharma',
            'role': 'citizen',
            'phone': '+919876543211',
            'city': 'Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'occupation': 'Student',
            'annual_income': 150000,
            'family_size': 3,
            'age': 22,
            'gender': 'female',
            'education': 'Graduate',
            'land_ownership': False,
            'has_ration_card': True,
            'profile_completed': True,
            'location': 'South Delhi, Delhi'
        },
        {
            'email': 'raj@janmitra.in',
            'password': 'citizen123',
            'name': 'Raj Patel',
            'role': 'citizen',
            'phone': '+919876543212',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'occupation': 'Business Owner',
            'annual_income': 800000,
            'family_size': 5,
            'age': 35,
            'gender': 'male',
            'education': 'Graduate',
            'land_ownership': False,
            'has_ration_card': False,
            'profile_completed': True,
            'location': 'Andheri, Mumbai'
        },
        {
            'email': 'gov@janmitra.in',
            'password': 'admin123',
            'name': 'National Officer',
            'role': 'government',
            'gov_level': 'national',
            'phone': '+919999999999',
            'city': 'New Delhi',
            'state': 'Delhi',
            'profile_completed': True,
            'location': 'Central Delhi'
        },
        {
            'email': 'officer@janmitra.in',
            'password': 'admin123',
            'name': 'District Collector Pune',
            'role': 'government',
            'gov_level': 'district',
            'phone': '+919999999998',
            'city': 'Pune',
            'district': 'Pune',
            'state': 'Maharashtra',
            'profile_completed': True,
            'location': 'Pune, Maharashtra'
        },
        {
            'email': 'state.officer@janmitra.in',
            'password': 'admin123',
            'name': 'State Officer Maharashtra',
            'role': 'government',
            'gov_level': 'state',
            'phone': '+919999999997',
            'state': 'Maharashtra',
            'profile_completed': True,
            'location': 'Maharashtra'
        }
    ]

    for user_data in users_data:
        existing = User.query.filter_by(email=user_data['email']).first()
        if existing:
            print(f"User {user_data['email']} already exists, updating...")
            for key, value in user_data.items():
                if key != 'password':
                    setattr(existing, key, value)
            existing.set_password(user_data['password'])
        else:
            password = user_data.pop('password')
            user = User(**user_data)
            user.set_password(password)
            user.last_login = datetime.utcnow()
            db.session.add(user)
            print(f"✅ Created user: {user.email}")

    db.session.commit()

    print("\n" + "="*50)
    print("DEMO USERS CREATED")
    print("="*50)
    print("\n🧑 CITIZENS:")
    print("  • ramesh@janmitra.in / citizen123 (Farmer, Punjab)")
    print("  • priya@janmitra.in / citizen123 (Student, Delhi)")
    print("  • raj@janmitra.in / citizen123 (Business, Mumbai)")
    print("\n🏛️ GOVERNMENT:")
    print("  • gov@janmitra.in / admin123 (National Officer)")
    print("  • state.officer@janmitra.in / admin123 (State Officer Maharashtra)")
    print("  • officer@janmitra.in / admin123 (District Collector Pune)")
    print("\n")
