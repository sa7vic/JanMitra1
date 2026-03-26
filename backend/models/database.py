from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
from sqlalchemy.orm import validates
from sqlalchemy import event, text

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='citizen', nullable=False)
    gov_level = db.Column(db.String(20))
    official_email = db.Column(db.String(120))
    department = db.Column(db.String(120))
    designation = db.Column(db.String(120))
    name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    state = db.Column(db.String(100), index=True)
    district = db.Column(db.String(100), index=True)
    city = db.Column(db.String(100), index=True)
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

    ALLOWED_ROLES = {'citizen', 'government', 'admin'}
    ALLOWED_GOV_LEVELS = {'national', 'state', 'district', 'local'}
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @validates('role')
    def validate_role(self, key, role):
        normalized = (role or 'citizen').strip().lower()
        if normalized == 'gov':
            normalized = 'government'
        if normalized not in self.ALLOWED_ROLES:
            raise ValueError('Invalid role. Allowed: citizen, government, admin')
        return normalized

    @validates('gov_level')
    def validate_gov_level(self, key, gov_level):
        if gov_level is None:
            return None

        normalized = gov_level.strip().lower()
        if normalized not in self.ALLOWED_GOV_LEVELS:
            raise ValueError('Invalid gov_level. Allowed: national, state, district, local')
        return normalized

    def validate_government_scope(self):
        if self.role != 'government':
            return

        if not self.gov_level:
            raise ValueError('gov_level is required for government users')

        if self.gov_level == 'state' and not self.state:
            raise ValueError('state is required for state-level government users')
        if self.gov_level == 'district' and (not self.state or not self.district):
            raise ValueError('state and district are required for district-level government users')
        if self.gov_level == 'local' and (not self.state or not self.district or not self.city):
            raise ValueError('state, district, and city are required for local-level government users')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'gov_level': self.gov_level,
            'official_email': self.official_email,
            'department': self.department,
            'designation': self.designation,
            'name': self.name,
            'location': self.location,
            'state': self.state,
            'district': self.district,
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
    __table_args__ = (
        db.Index('idx_citizen_report_state_district_city', 'state', 'district', 'city'),
        db.Index('idx_citizen_report_created_at', 'created_at'),
        db.Index('idx_citizen_report_lat_lon', 'latitude', 'longitude'),
        db.Index('idx_citizen_report_type_status', 'report_type', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    report_type = db.Column(db.String(50))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    data = db.Column(db.Text)
    location = db.Column(db.String(200))
    state = db.Column(db.String(100), index=True)
    district = db.Column(db.String(100), index=True)
    city = db.Column(db.String(100), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False)
    verification_confidence = db.Column(db.Float, default=0.0)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.String(20), default='medium')
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    image_url = db.Column(db.String(255))
    photo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='reports')
    assigned_user = db.relationship('User', foreign_keys=[assigned_to])
    assigned_by_user = db.relationship('User', foreign_keys=[assigned_by])
    
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
            'district': self.district,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'verified': self.verified,
            'verification_confidence': self.verification_confidence,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'assigned_by': self.assigned_by,
            'assigned_to_name': self.assigned_user.name if self.assigned_user else None,
            'assigned_to_level': self.assigned_user.gov_level if self.assigned_user else None,
            'image_url': self.image_url or self.photo_url,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat()
        }


class ReportAuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('citizen_report.id'), nullable=False, index=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(30), nullable=False)  # assigned, status_changed
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20))
    from_assigned_to = db.Column(db.Integer)
    to_assigned_to = db.Column(db.Integer)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('CitizenReport', backref='audit_logs')
    actor = db.relationship('User', foreign_keys=[actor_user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'actor_user_id': self.actor_user_id,
            'actor_name': self.actor.name if self.actor else None,
            'action': self.action,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'from_assigned_to': self.from_assigned_to,
            'to_assigned_to': self.to_assigned_to,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
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

class WhatsAppConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    message_type = db.Column(db.String(20), default='incoming')  # incoming or outgoing
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, processed, failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='whatsapp_conversations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'message': self.message,
            'response': self.response,
            'message_type': self.message_type,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }


@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def validate_user_government_fields(mapper, connection, target):
    # Enforce scope constraints on all write paths, not just auth routes.
    target.validate_government_scope()


def _sqlite_add_missing_columns():
    """Backfill new columns for existing SQLite databases without Alembic."""
    if db.engine.dialect.name != 'sqlite':
        return

    user_columns = {
        row['name']
        for row in db.session.execute(text("PRAGMA table_info('user')")).mappings().all()
    }
    report_columns = {
        row['name']
        for row in db.session.execute(text("PRAGMA table_info('citizen_report')")).mappings().all()
    }

    if 'gov_level' not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN gov_level VARCHAR(20)"))
    if 'district' not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN district VARCHAR(100)"))
    if 'official_email' not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN official_email VARCHAR(120)"))
    if 'department' not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN department VARCHAR(120)"))
    if 'designation' not in user_columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN designation VARCHAR(120)"))

    if 'district' not in report_columns:
        db.session.execute(text("ALTER TABLE citizen_report ADD COLUMN district VARCHAR(100)"))
    if 'assigned_to' not in report_columns:
        db.session.execute(text("ALTER TABLE citizen_report ADD COLUMN assigned_to INTEGER"))
    if 'assigned_by' not in report_columns:
        db.session.execute(text("ALTER TABLE citizen_report ADD COLUMN assigned_by INTEGER"))
    if 'image_url' not in report_columns:
        db.session.execute(text("ALTER TABLE citizen_report ADD COLUMN image_url VARCHAR(255)"))
    if 'latitude' not in report_columns:
        db.session.execute(text("ALTER TABLE citizen_report ADD COLUMN latitude FLOAT"))
    if 'longitude' not in report_columns:
        db.session.execute(text("ALTER TABLE citizen_report ADD COLUMN longitude FLOAT"))

    db.session.execute(text("""
        UPDATE citizen_report
        SET image_url = photo_url
        WHERE (image_url IS NULL OR image_url = '') AND photo_url IS NOT NULL
    """))

    # SQLite supports IF NOT EXISTS for index creation in modern versions.
    db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_user_state ON user(state)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_user_district ON user(district)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_user_city ON user(city)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_citizen_report_district ON citizen_report(district)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_citizen_report_assigned_to ON citizen_report(assigned_to)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_citizen_report_lat_lon ON citizen_report(latitude, longitude)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_citizen_report_type_status ON citizen_report(report_type, status)"))

    db.session.commit()


def _postgres_enable_postgis_and_spatial_index():
    """Enable PostGIS and keep geom in sync with latitude/longitude on PostgreSQL."""
    if db.engine.dialect.name != 'postgresql':
        return

    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    db.session.execute(text("ALTER TABLE citizen_report ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326)"))

    db.session.execute(text("""
        UPDATE citizen_report
        SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
          AND (geom IS NULL OR ST_X(geom) != longitude OR ST_Y(geom) != latitude)
    """))

    db.session.execute(text("""
        CREATE OR REPLACE FUNCTION sync_citizen_report_geom()
        RETURNS trigger AS $$
        BEGIN
            IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
                NEW.geom = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
            ELSE
                NEW.geom = NULL;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    db.session.execute(text("DROP TRIGGER IF EXISTS trg_sync_citizen_report_geom ON citizen_report"))
    db.session.execute(text("""
        CREATE TRIGGER trg_sync_citizen_report_geom
        BEFORE INSERT OR UPDATE OF latitude, longitude
        ON citizen_report
        FOR EACH ROW
        EXECUTE FUNCTION sync_citizen_report_geom()
    """))

    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_citizen_report_geom ON citizen_report USING GIST (geom)"))
    db.session.commit()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _postgres_enable_postgis_and_spatial_index()
        _sqlite_add_missing_columns()
        print("✅ Database initialized!")