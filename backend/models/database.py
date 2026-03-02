from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='citizen')
    name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    occupation = db.Column(db.String(100))
    annual_income = db.Column(db.Integer)
    family_size = db.Column(db.Integer)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    education = db.Column(db.String(100))
    land_ownership = db.Column(db.Boolean, default=False)
    has_ration_card = db.Column(db.Boolean, default=False)
    aadhaar_verified = db.Column(db.Boolean, default=False)
    profile_completed = db.Column(db.Boolean, default=False)
    onboarding_step = db.Column(db.Integer, default=0)
    preferences = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    reputation_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'name': self.name,
            'location': self.location,
            'state': self.state,
            'city': self.city,
            'pincode': self.pincode,
            'occupation': self.occupation,
            'annual_income': self.annual_income,
            'family_size': self.family_size,
            'age': self.age,
            'gender': self.gender,
            'education': self.education,
            'land_ownership': self.land_ownership,
            'has_ration_card': self.has_ration_card,
            'aadhaar_verified': self.aadhaar_verified,
            'profile_completed': self.profile_completed,
            'onboarding_step': self.onboarding_step,
            'preferences': json.loads(self.preferences) if self.preferences else {},
            'verified': self.verified,
            'reputation_score': self.reputation_score,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def get_profile_completeness(self):
        fields = [
            self.name, self.location, self.state, self.city, 
            self.occupation, self.annual_income, self.family_size,
            self.age, self.gender
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(200))
    url = db.Column(db.String(500), unique=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100))
    sentiment = db.Column(db.Float, default=0.0)
    importance = db.Column(db.Float, default=0.5)
    processed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'url': self.url,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'category': self.category,
            'sentiment': self.sentiment,
            'importance': self.importance
        }

class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    type = db.Column(db.String(50))
    description = db.Column(db.Text)
    data = db.Column(db.Text)
    importance_score = db.Column(db.Float, default=0.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'data': json.loads(self.data) if self.data else {},
            'importance_score': self.importance_score,
            'updated_at': self.updated_at.isoformat()
        }

class Relationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=False)
    relationship_type = db.Column(db.String(100))
    strength = db.Column(db.Float, default=0.5)
    context = db.Column(db.Text)
    bidirectional = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    source = db.relationship('Entity', foreign_keys=[source_id])
    target = db.relationship('Entity', foreign_keys=[target_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source.name,
            'target': self.target.name,
            'type': self.relationship_type,
            'strength': self.strength,
            'context': self.context
        }

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    severity = db.Column(db.String(20))
    confidence = db.Column(db.Float)
    predicted_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    affected_radius = db.Column(db.Integer)
    status = db.Column(db.String(20), default='active')
    evidence = db.Column(db.Text)
    impact_estimate = db.Column(db.Text)
    recommended_actions = db.Column(db.Text)
    affected_population = db.Column(db.Integer)
    economic_impact = db.Column(db.Float)
    validated = db.Column(db.Boolean, default=False)
    accuracy_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'confidence': self.confidence,
            'predicted_date': self.predicted_date.isoformat() if self.predicted_date else None,
            'location': self.location,
            'state': self.state,
            'city': self.city,
            'affected_radius': self.affected_radius,
            'status': self.status,
            'evidence': json.loads(self.evidence) if self.evidence else {},
            'impact_estimate': json.loads(self.impact_estimate) if self.impact_estimate else {},
            'recommended_actions': json.loads(self.recommended_actions) if self.recommended_actions else [],
            'affected_population': self.affected_population,
            'economic_impact': self.economic_impact,
            'created_at': self.created_at.isoformat()
        }

class CitizenReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    report_type = db.Column(db.String(50))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    data = db.Column(db.Text)
    location = db.Column(db.String(200))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False)
    verification_confidence = db.Column(db.Float, default=0.0)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.String(20), default='medium')
    photo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'title': self.title,
            'description': self.description,
            'data': json.loads(self.data) if self.data else {},
            'location': self.location,
            'state': self.state,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'verified': self.verified,
            'verification_confidence': self.verification_confidence,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'status': self.status,
            'priority': self.priority,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat()
        }

class UserAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    prediction_id = db.Column(db.Integer, db.ForeignKey('prediction.id'))
    alert_type = db.Column(db.String(50))
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    severity = db.Column(db.String(20))
    read = db.Column(db.Boolean, default=False)
    dismissed = db.Column(db.Boolean, default=False)
    actionable = db.Column(db.Boolean, default=True)
    action_taken = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='alerts')
    prediction = db.relationship('Prediction', backref='user_alerts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prediction_id': self.prediction_id,
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'read': self.read,
            'dismissed': self.dismissed,
            'actionable': self.actionable,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat()
        }

class Scheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    eligibility_criteria = db.Column(db.Text)
    benefits = db.Column(db.Text)
    documents_required = db.Column(db.Text)
    how_to_apply = db.Column(db.Text)
    application_process = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    url = db.Column(db.String(500))
    ministry = db.Column(db.String(200))
    target_beneficiaries = db.Column(db.Integer)
    budget_allocated = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'description': self.description,
            'category': self.category,
            'eligibility_criteria': json.loads(self.eligibility_criteria) if self.eligibility_criteria else {},
            'benefits': self.benefits,
            'documents_required': json.loads(self.documents_required) if self.documents_required else [],
            'how_to_apply': self.how_to_apply,
            'application_process': json.loads(self.application_process) if self.application_process else [],
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'url': self.url,
            'ministry': self.ministry,
            'priority': self.priority,
            'active': self.active
        }

class UserScheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    scheme_id = db.Column(db.Integer, db.ForeignKey('scheme.id'))
    status = db.Column(db.String(50), default='eligible')
    match_score = db.Column(db.Float)
    applied_at = db.Column(db.DateTime)
    application_id = db.Column(db.String(100))
    application_status = db.Column(db.String(50))
    enrollment_date = db.Column(db.DateTime)
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)
    total_benefit_received = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='user_schemes')
    scheme = db.relationship('Scheme', backref='enrollments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scheme_id': self.scheme_id,
            'scheme': self.scheme.to_dict() if self.scheme else None,
            'status': self.status,
            'match_score': self.match_score,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'application_id': self.application_id,
            'application_status': self.application_status,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'next_payment_date': self.next_payment_date.isoformat() if self.next_payment_date else None,
            'total_benefit_received': self.total_benefit_received
        }

class FactCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claim = db.Column(db.Text, nullable=False)
    verdict = db.Column(db.String(20))
    confidence = db.Column(db.Float)
    explanation = db.Column(db.Text)
    sources = db.Column(db.Text)
    evidence = db.Column(db.Text)
    category = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    helpful_count = db.Column(db.Integer, default=0)
    shared_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='fact_checks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'claim': self.claim,
            'verdict': self.verdict,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'sources': json.loads(self.sources) if self.sources else [],
            'evidence': json.loads(self.evidence) if self.evidence else {},
            'category': self.category,
            'helpful_count': self.helpful_count,
            'shared_count': self.shared_count,
            'created_at': self.created_at.isoformat()
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("✅ Database initialized!")