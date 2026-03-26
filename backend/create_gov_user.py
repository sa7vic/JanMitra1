from app import app
from models.database import db, User

with app.app_context():
    # Check if exists
    gov = User.query.filter_by(email='gov@janmitra.in').first()

    if not gov:
        gov = User(
            email='gov@janmitra.in',
            name='Government Admin',
            role='government',
            gov_level='national',
            phone='+919999999999'
        )
        gov.set_password('admin123')
        db.session.add(gov)
        db.session.commit()
        print("✅ Government user created!")
        print("Email: gov@janmitra.in")
        print("Password: admin123")
    else:
        if gov.role != 'government':
            gov.role = 'government'
        if not gov.gov_level:
            gov.gov_level = 'national'
            db.session.commit()
        print("Government user already exists")
