from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from models.database import db, init_db, Article, Entity, Relationship, Prediction, User, CitizenReport, Scheme, FactCheck, UserAlert, UserScheme
from services.data_collector import DataCollector
from services.ai_processor import AIProcessor
from services.auto_scheduler import start_scheduler
from services.crisis_predictor import CrisisPredictor
from services.fact_checker import FactChecker
from services.scheme_matcher import SchemeMatcher
from services.citizen_intel import CitizenIntel
from services.alert_generator import AlertGenerator
from routes.auth import auth_bp
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'janmitra-jwt-secret-key-change-in-production')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

os.makedirs('data', exist_ok=True)

init_db(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')

collector = DataCollector()
ai_processor = AIProcessor()
crisis_predictor = CrisisPredictor()
fact_checker = FactChecker()
scheme_matcher = SchemeMatcher(app)
citizen_intel = CitizenIntel()
alert_generator = AlertGenerator()

scheduler = start_scheduler(app)

@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'message': 'JanMitra API is running',
        'version': '2.0.0'
    })

@app.route('/api/stats')
def get_stats():
    stats = {
        'articles': Article.query.count(),
        'entities': Entity.query.count(),
        'relationships': Relationship.query.count(),
        'predictions': Prediction.query.filter_by(status='active').count(),
        'users': User.query.count(),
        'reports': CitizenReport.query.filter_by(verified=True).count(),
        'schemes': Scheme.query.filter_by(active=True).count(),
        'last_updated': Article.query.order_by(Article.created_at.desc()).first().created_at.isoformat() if Article.query.first() else None
    }
    return jsonify(stats)

@app.route('/api/user/dashboard', methods=['GET'])
@jwt_required()
def get_user_dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    alert_generator.generate_alerts_for_user(user.id)
    alerts = alert_generator.get_user_alerts(user.id, include_read=False)
    
    scheme_matcher.match_schemes_for_user(user.id)
    enrolled_schemes = scheme_matcher.get_enrolled_schemes(user.id)
    eligible_schemes = scheme_matcher.get_eligible_schemes(user.id)[:5]
    
    user_reports = citizen_intel.get_user_reports(user.id)
    
    trending_issues = citizen_intel.get_trending_issues(
        city=user.city,
        state=user.state,
        limit=5
    )
    
    if user.city:
        prices = citizen_intel.get_aggregated_prices(city=user.city)
    else:
        prices = {}
    
    dashboard_data = {
        'user': user.to_dict(),
        'profile_completeness': user.get_profile_completeness(),
        'alerts': alerts[:5],
        'enrolled_schemes': enrolled_schemes,
        'eligible_schemes': eligible_schemes,
        'my_reports': user_reports[:5],
        'trending_issues': trending_issues,
        'local_prices': prices,
        'reputation_score': user.reputation_score
    }
    
    return jsonify(dashboard_data)

@app.route('/api/user/alerts', methods=['GET'])
@jwt_required()
def get_user_alerts():
    current_user_id = get_jwt_identity()
    
    include_read = request.args.get('include_read', 'false').lower() == 'true'
    
    alert_generator.generate_alerts_for_user(int(current_user_id))
    alerts = alert_generator.get_user_alerts(int(current_user_id), include_read)
    
    return jsonify({'alerts': alerts})

@app.route('/api/user/alerts/<int:alert_id>/read', methods=['POST'])
@jwt_required()
def mark_alert_read(alert_id):
    current_user_id = get_jwt_identity()
    
    success = alert_generator.mark_alert_read(alert_id, int(current_user_id))
    
    if success:
        return jsonify({'message': 'Alert marked as read'})
    return jsonify({'error': 'Alert not found'}), 404

@app.route('/api/user/alerts/<int:alert_id>/dismiss', methods=['POST'])
@jwt_required()
def dismiss_alert(alert_id):
    current_user_id = get_jwt_identity()
    
    success = alert_generator.dismiss_alert(alert_id, int(current_user_id))
    
    if success:
        return jsonify({'message': 'Alert dismissed'})
    return jsonify({'error': 'Alert not found'}), 404

@app.route('/api/user/alerts/<int:alert_id>/action-taken', methods=['POST'])
@jwt_required()
def alert_action_taken(alert_id):
    current_user_id = get_jwt_identity()
    
    success = alert_generator.mark_action_taken(alert_id, int(current_user_id))
    
    if success:
        return jsonify({'message': 'Action marked'})
    return jsonify({'error': 'Alert not found'}), 404

@app.route('/api/user/schemes', methods=['GET'])
@jwt_required()
def get_user_schemes():
    current_user_id = get_jwt_identity()
    
    scheme_matcher.match_schemes_for_user(int(current_user_id))
    
    enrolled = scheme_matcher.get_enrolled_schemes(int(current_user_id))
    eligible = scheme_matcher.get_eligible_schemes(int(current_user_id))
    
    return jsonify({
        'enrolled': enrolled,
        'eligible': eligible
    })

@app.route('/api/schemes/<int:scheme_id>', methods=['GET'])
def get_scheme_detail(scheme_id):
    scheme = Scheme.query.get(scheme_id)
    
    if not scheme:
        return jsonify({'error': 'Scheme not found'}), 404
    
    return jsonify(scheme.to_dict())

@app.route('/api/reports', methods=['GET', 'POST'])
def handle_reports():
    if request.method == 'POST':
        try:
            current_user_id = get_jwt_identity()
            user_id = int(current_user_id)
        except:
            return jsonify({'error': 'Authentication required'}), 401
        
        report_data = request.json
        report = citizen_intel.submit_report(user_id, report_data)
        
        return jsonify({
            'message': 'Report submitted successfully',
            'report': report
        })
    
    else:
        filters = {
            'city': request.args.get('city'),
            'state': request.args.get('state'),
            'report_type': request.args.get('type'),
            'verified_only': request.args.get('verified', 'false').lower() == 'true',
            'priority': request.args.get('priority'),
            'status': request.args.get('status'),
            'time_range': int(request.args.get('time_range', 168))
        }
        
        reports = citizen_intel.get_reports(filters)
        
        return jsonify({'reports': reports})

@app.route('/api/reports/<int:report_id>/upvote', methods=['POST'])
@jwt_required()
def upvote_report(report_id):
    current_user_id = get_jwt_identity()
    
    report = citizen_intel.upvote_report(report_id, int(current_user_id))
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    return jsonify({
        'message': 'Upvoted successfully',
        'report': report
    })

@app.route('/api/reports/<int:report_id>/downvote', methods=['POST'])
@jwt_required()
def downvote_report(report_id):
    current_user_id = get_jwt_identity()
    
    report = citizen_intel.downvote_report(report_id, int(current_user_id))
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    return jsonify({
        'message': 'Downvoted successfully',
        'report': report
    })

@app.route('/api/trending-issues', methods=['GET'])
def get_trending_issues():
    city = request.args.get('city')
    state = request.args.get('state')
    limit = int(request.args.get('limit', 10))
    
    trending = citizen_intel.get_trending_issues(city, state, limit)
    
    return jsonify({'trending': trending})

@app.route('/api/prices', methods=['GET'])
def get_prices():
    city = request.args.get('city')
    state = request.args.get('state')
    item = request.args.get('item')
    
    prices = citizen_intel.get_aggregated_prices(city, state, item)
    
    return jsonify({'prices': prices})

@app.route('/api/predictions')
def get_predictions():
    status = request.args.get('status', 'active')
    city = request.args.get('city')
    state = request.args.get('state')
    category = request.args.get('category')
    
    query = Prediction.query.filter_by(status=status)
    
    if city:
        query = query.filter_by(city=city)
    elif state:
        query = query.filter_by(state=state)
    
    if category:
        query = query.filter_by(category=category)
    
    predictions = query.order_by(Prediction.confidence.desc()).all()
    
    return jsonify({
        'predictions': [p.to_dict() for p in predictions]
    })

@app.route('/api/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction_detail(prediction_id):
    prediction = Prediction.query.get(prediction_id)
    
    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404
    
    related_reports = CitizenReport.query.filter_by(
        city=prediction.city,
        verified=True
    ).limit(20).all()
    
    return jsonify({
        'prediction': prediction.to_dict(),
        'related_reports': [r.to_dict() for r in related_reports]
    })

@app.route('/api/query', methods=['POST', 'OPTIONS'])
def query():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        answer = ai_processor.answer_question(question)
        
        response = {
            'question': question,
            'answer': answer
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in query endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/fact-check', methods=['POST'])
def fact_check():
    data = request.json
    claim = data.get('claim', '')
    
    if not claim:
        return jsonify({'error': 'Claim is required'}), 400
    
    user_id = None
    try:
        current_user_id = get_jwt_identity()
        user_id = int(current_user_id)
    except:
        pass
    
    result = fact_checker.verify_claim(claim, user_id)
    
    return jsonify(result)

@app.route('/api/fact-checks')
def get_fact_checks():
    limit = request.args.get('limit', 20, type=int)
    
    fact_checks = FactCheck.query.order_by(FactCheck.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'fact_checks': [fc.to_dict() for fc in fact_checks]
    })

@app.route('/api/entities')
def get_entities():
    limit = request.args.get('limit', 100, type=int)
    entity_type = request.args.get('type', None)
    
    query = Entity.query
    if entity_type:
        query = query.filter_by(type=entity_type)
    
    entities = query.order_by(Entity.updated_at.desc()).limit(limit).all()
    
    return jsonify({
        'entities': [e.to_dict() for e in entities]
    })

@app.route('/api/relationships')
def get_relationships():
    limit = request.args.get('limit', 200, type=int)
    
    relationships = Relationship.query.order_by(Relationship.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'relationships': [r.to_dict() for r in relationships]
    })

@app.route('/api/knowledge-graph')
def get_knowledge_graph():
    entities = Entity.query.limit(100).all()
    relationships = Relationship.query.limit(200).all()
    
    nodes = [
        {
            'id': e.id,
            'label': e.name,
            'type': e.type,
            'description': e.description
        }
        for e in entities
    ]
    
    edges = [
        {
            'source': r.source_id,
            'target': r.target_id,
            'type': r.relationship_type,
            'strength': r.strength
        }
        for r in relationships
    ]
    
    return jsonify({
        'nodes': nodes,
        'edges': edges
    })

@app.route('/api/news')
def get_news():
    limit = request.args.get('limit', 20, type=int)
    category = request.args.get('category', None)
    
    query = Article.query
    if category:
        query = query.filter_by(category=category)
    
    articles = query.order_by(Article.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'articles': [a.to_dict() for a in articles]
    })

if __name__ == '__main__':
    print("\n🚀 Starting JanMitra Backend v2.0...")
    print("📊 Dashboard: http://localhost:5000")
    print("📡 API: http://localhost:5000/api/stats")
    print("⏰ Auto-collection: Every hour")
    print("🔍 All features loaded\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')