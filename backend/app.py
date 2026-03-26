from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from collections import Counter
import math
from datetime import UTC, datetime, timedelta
from sqlalchemy import text
from config import Config
from models.database import db, init_db, Article, Entity, Relationship, Prediction, User, CitizenReport, Scheme, FactCheck, ReportAuditLog
from services.data_collector import DataCollector
from services.ai_processor import AIProcessor
from services.auto_scheduler import start_scheduler
from services.crisis_predictor import CrisisPredictor
from services.fact_checker import FactChecker
from services.scheme_matcher import SchemeMatcher
from services.citizen_intel import CitizenIntel
from services.alert_generator import AlertGenerator
from services.graph_reasoner import GraphReasoningService
from services.geocoding_service import GeocodingService
from services.upload_service import validate_image_file, upload_report_image
from routes.auth import auth_bp
from routes.whatsapp import whatsapp_bp
from utils.geo import haversine_km, parse_bbox
from utils.locations import get_states, get_districts, get_cities
import os

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'janmitra-jwt-secret-key-change-in-production')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000", 
            "http://127.0.0.1:3000", 
            "http://localhost:5173", 
            "http://127.0.0.1:5173",
            "https://jan-mitra1.vercel.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

os.makedirs('data', exist_ok=True)

init_db(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')

collector = DataCollector()
ai_processor = AIProcessor()
crisis_predictor = CrisisPredictor()
fact_checker = FactChecker()
scheme_matcher = SchemeMatcher(app)
citizen_intel = CitizenIntel()
alert_generator = AlertGenerator()
graph_reasoner = GraphReasoningService()
geocoding_service = GeocodingService()

scheduler = start_scheduler(app)


def _normalized_role(user):
    role = (user.role or 'citizen').strip().lower()
    if role == 'gov':
        return 'government'
    return role


def government_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if _normalized_role(user) != 'government':
            return jsonify({'error': 'Forbidden. Government role required.'}), 403

        return fn(user, *args, **kwargs)

    return wrapper


GOV_LEVEL_RANK = {
    'national': 0,
    'state': 1,
    'district': 2,
    'local': 3,
}

VALID_REPORT_STATUSES = {'pending', 'working', 'completed'}
STATUS_TRANSITIONS = {
    'pending': {'working'},
    'working': {'completed'},
    'completed': set(),
}


def _in_user_scope(user, report):
    gov_level = (user.gov_level or '').strip().lower()
    if gov_level == 'national':
        return True
    if gov_level == 'state':
        return bool(user.state and report.state == user.state)
    if gov_level == 'district':
        return bool(
            user.state and user.district and
            report.state == user.state and
            report.district == user.district
        )
    if gov_level == 'local':
        return bool(
            user.state and user.district and user.city and
            report.state == user.state and
            report.district == user.district and
            report.city == user.city
        )
    return False


def _is_same_or_lower_authority(assigner, assignee):
    assigner_rank = GOV_LEVEL_RANK.get((assigner.gov_level or '').strip().lower(), 99)
    assignee_rank = GOV_LEVEL_RANK.get((assignee.gov_level or '').strip().lower(), 99)
    return assignee_rank >= assigner_rank


def _within_assigner_jurisdiction(assigner, assignee):
    level = (assigner.gov_level or '').strip().lower()
    if level == 'national':
        return True
    if level == 'state':
        return bool(assigner.state and assignee.state == assigner.state)
    if level == 'district':
        return bool(
            assigner.state and assigner.district and
            assignee.state == assigner.state and
            assignee.district == assigner.district
        )
    if level == 'local':
        return bool(
            assigner.state and assigner.district and assigner.city and
            assignee.state == assigner.state and
            assignee.district == assigner.district and
            assignee.city == assigner.city
        )
    return False


def _is_higher_authority(current_user, assigned_user):
    current_rank = GOV_LEVEL_RANK.get((current_user.gov_level or '').strip().lower(), 99)
    assigned_rank = GOV_LEVEL_RANK.get((assigned_user.gov_level or '').strip().lower(), 99)
    return current_rank < assigned_rank


def _same_jurisdiction_for_control(current_user, assigned_user):
    # Higher authority can manage subordinate only if they overlap in jurisdiction.
    return _within_assigner_jurisdiction(current_user, assigned_user)


def _serialize_report_detail(report):
    assigned_user = report.assigned_user
    return {
        'id': report.id,
        'title': report.title,
        'description': report.description,
        'report_type': report.report_type,
        'state': report.state,
        'district': report.district,
        'city': report.city,
        'location': report.location,
        'status': report.status,
        'image_url': report.image_url or report.photo_url,
        'assigned_to': report.assigned_to,
        'assigned_to_user': {
            'id': assigned_user.id,
            'name': assigned_user.name,
            'email': assigned_user.email,
            'gov_level': assigned_user.gov_level,
            'state': assigned_user.state,
            'district': assigned_user.district,
            'city': assigned_user.city,
        } if assigned_user else None,
        'created_at': report.created_at.isoformat() if report.created_at else None,
    }


def _parse_float(value):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_bool(value):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {'true', '1', 'yes'}:
        return True
    if normalized in {'false', '0', 'no'}:
        return False
    return None


def _build_location_query_from_report_payload(report_data):
    if not report_data:
        return None

    parts = [
        report_data.get('location'),
        report_data.get('city'),
        report_data.get('district'),
        report_data.get('state'),
        'India',
    ]
    values = [str(part).strip() for part in parts if part and str(part).strip()]
    if not values:
        return None
    return ', '.join(values)


def _apply_government_scope(query, user):
    gov_level = (user.gov_level or '').strip().lower()
    if not gov_level:
        return None, jsonify({'error': 'Government profile is incomplete: gov_level is required'}), 400

    if gov_level == 'national':
        return query, None, None
    if gov_level == 'state':
        if not user.state:
            return None, jsonify({'error': 'Government profile is incomplete: state is required for state level'}), 400
        return query.filter(CitizenReport.state == user.state), None, None
    if gov_level == 'district':
        if not user.state or not user.district:
            return None, jsonify({'error': 'Government profile is incomplete: state and district are required for district level'}), 400
        return query.filter(
            CitizenReport.state == user.state,
            CitizenReport.district == user.district,
        ), None, None
    if gov_level == 'local':
        if not user.state or not user.district or not user.city:
            return None, jsonify({'error': 'Government profile is incomplete: state, district, and city are required for local level'}), 400
        return query.filter(
            CitizenReport.state == user.state,
            CitizenReport.district == user.district,
            CitizenReport.city == user.city,
        ), None, None

    return None, jsonify({'error': 'Invalid gov_level for current user'}), 400


def _apply_common_report_filters(query):
    status = request.args.get('status')
    report_type = request.args.get('type') or request.args.get('category')
    verified = _parse_bool(request.args.get('verified'))
    state = request.args.get('state')
    district = request.args.get('district')
    city = request.args.get('city')
    time_range = request.args.get('time_range', type=int)

    if status:
        query = query.filter(CitizenReport.status == status)
    if report_type:
        query = query.filter(CitizenReport.report_type == report_type)
    if verified is not None:
        query = query.filter(CitizenReport.verified == verified)
    if state:
        query = query.filter(CitizenReport.state == state)
    if district:
        query = query.filter(CitizenReport.district == district)
    if city:
        query = query.filter(CitizenReport.city == city)
    if time_range and time_range > 0:
        time_limit = datetime.now(UTC) - timedelta(hours=time_range)
        query = query.filter(CitizenReport.created_at >= time_limit)

    return query


def _generate_circle_polygon(lon, lat, radius_km, vertices=24):
    ring = []
    safe_radius = max(0.5, float(radius_km))
    for index in range(vertices):
        theta = 2.0 * math.pi * (index / vertices)
        lat_offset = (safe_radius / 111.0) * math.sin(theta)
        lon_offset = (
            (safe_radius / max(1e-6, 111.0 * abs(math.cos(math.radians(lat)))))
            * math.cos(theta)
        )
        ring.append([lon + lon_offset, lat + lat_offset])
    if ring:
        ring.append(ring[0])
    return ring


def _compute_spatial_clusters(points, eps_km=4.0, min_points=3):
    """Distance-based clustering similar to DBSCAN for demo-safe server analytics."""
    if not points:
        return [], []

    neighbors = {}
    for idx, point in enumerate(points):
        nearby = []
        for jdx, candidate in enumerate(points):
            distance = haversine_km(
                point['latitude'],
                point['longitude'],
                candidate['latitude'],
                candidate['longitude'],
            )
            if distance <= eps_km:
                nearby.append(jdx)
        neighbors[idx] = nearby

    visited = set()
    assigned = {}
    clusters = []

    def expand(seed_idx, cluster_id):
        queue = [seed_idx]
        cluster_members = []

        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)

            current_neighbors = neighbors[current]
            if len(current_neighbors) >= min_points:
                for n_idx in current_neighbors:
                    if n_idx not in visited:
                        queue.append(n_idx)

            if current not in assigned:
                assigned[current] = cluster_id
                cluster_members.append(current)

        return cluster_members

    for idx in range(len(points)):
        if idx in visited:
            continue

        if len(neighbors[idx]) < min_points:
            continue

        cluster_id = len(clusters) + 1
        members = expand(idx, cluster_id)
        if members:
            clusters.append(members)

    noise = []
    for idx, point in enumerate(points):
        if idx not in assigned:
            point['cluster_id'] = None
            noise.append(point['id'])
        else:
            point['cluster_id'] = assigned[idx]

    cluster_payload = []
    for cluster_idx, member_indexes in enumerate(clusters, start=1):
        cluster_points = [points[m_idx] for m_idx in member_indexes]
        if not cluster_points:
            continue

        center_lat = sum(row['latitude'] for row in cluster_points) / len(cluster_points)
        center_lon = sum(row['longitude'] for row in cluster_points) / len(cluster_points)
        min_lat = min(row['latitude'] for row in cluster_points)
        max_lat = max(row['latitude'] for row in cluster_points)
        min_lon = min(row['longitude'] for row in cluster_points)
        max_lon = max(row['longitude'] for row in cluster_points)

        lat_span_km = max(0.5, (max_lat - min_lat) * 111.0)
        lon_span_km = max(0.5, (max_lon - min_lon) * 111.0 * abs(math.cos(math.radians(center_lat))))
        area_km2 = max(0.25, lat_span_km * lon_span_km)
        density = len(cluster_points) / area_km2

        cluster_payload.append({
            'cluster_id': cluster_idx,
            'size': len(cluster_points),
            'density_per_km2': round(density, 3),
            'area_km2': round(area_km2, 3),
            'center': {
                'latitude': round(center_lat, 6),
                'longitude': round(center_lon, 6),
            },
            'bbox': [
                round(min_lon, 6),
                round(min_lat, 6),
                round(max_lon, 6),
                round(max_lat, 6),
            ],
            'top_category': Counter(
                row.get('report_type') or 'unknown'
                for row in cluster_points
            ).most_common(1)[0][0],
            'point_ids': [row['id'] for row in cluster_points],
        })

    cluster_payload.sort(
        key=lambda row: (row['density_per_km2'], row['size']),
        reverse=True,
    )
    return cluster_payload, noise


def _build_region_overlays(points):
    by_region = {}
    for point in points:
        region_name = point.get('district') or point.get('city') or point.get('state') or 'Unknown'
        by_region.setdefault(region_name, []).append(point)

    if not by_region:
        return {
            'type': 'FeatureCollection',
            'features': [],
        }, []

    max_count = max(len(rows) for rows in by_region.values())
    features = []
    ranked_regions = []

    for region_name, rows in by_region.items():
        center_lat = sum(row['latitude'] for row in rows) / len(rows)
        center_lon = sum(row['longitude'] for row in rows) / len(rows)

        spread = 0.0
        for row in rows:
            spread = max(
                spread,
                haversine_km(center_lat, center_lon, row['latitude'], row['longitude']),
            )

        radius_km = max(2.0, min(25.0, spread * 1.6 + 2.0))
        intensity = (len(rows) / max_count) if max_count else 0.0

        polygon = _generate_circle_polygon(center_lon, center_lat, radius_km)
        features.append({
            'type': 'Feature',
            'properties': {
                'region': region_name,
                'count': len(rows),
                'intensity': round(intensity, 3),
                'radius_km': round(radius_km, 3),
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [polygon],
            },
        })

        ranked_regions.append({
            'region': region_name,
            'count': len(rows),
            'intensity': round(intensity, 3),
        })

    ranked_regions.sort(key=lambda row: row['count'], reverse=True)
    return {
        'type': 'FeatureCollection',
        'features': features,
    }, ranked_regions


def _compute_temporal_spikes(points):
    if not points:
        return []

    now = datetime.now(UTC)
    recent_from = now - timedelta(hours=24)
    previous_from = now - timedelta(hours=48)

    region_windows = {}
    for point in points:
        region = point.get('district') or point.get('city') or point.get('state') or 'Unknown'
        region_windows.setdefault(region, {'recent': 0, 'previous': 0})

        created_at_raw = point.get('created_at')
        if not created_at_raw:
            continue

        try:
            created_at = datetime.fromisoformat(created_at_raw)
        except ValueError:
            continue

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        if created_at >= recent_from:
            region_windows[region]['recent'] += 1
        elif previous_from <= created_at < recent_from:
            region_windows[region]['previous'] += 1

    spikes = []
    for region, window in region_windows.items():
        recent = window['recent']
        previous = window['previous']
        if recent >= 3 and recent >= (previous * 2 if previous > 0 else 3):
            spikes.append({
                'region': region,
                'recent_24h': recent,
                'previous_24h': previous,
                'delta': recent - previous,
                'growth_ratio': round(recent / max(1, previous), 2),
            })

    spikes.sort(key=lambda row: (row['delta'], row['recent_24h']), reverse=True)
    return spikes[:5]

@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'message': 'JanMitra API is running',
        'version': '2.0.0'
    })


@app.route('/api/locations/states', methods=['GET'])
def get_location_states():
    return jsonify({'states': get_states()})


@app.route('/api/locations/districts', methods=['GET'])
def get_location_districts():
    state = request.args.get('state', '').strip()
    if not state:
        return jsonify({'error': 'state is required'}), 400
    return jsonify({'districts': get_districts(state)})


@app.route('/api/locations/cities', methods=['GET'])
def get_location_cities():
    state = request.args.get('state', '').strip()
    district = request.args.get('district', '').strip()
    if not state or not district:
        return jsonify({'error': 'state and district are required'}), 400
    return jsonify({'cities': get_cities(state, district)})

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
    user = db.session.get(User, int(current_user_id))
    
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
    scheme = db.session.get(Scheme, scheme_id)
    
    if not scheme:
        return jsonify({'error': 'Scheme not found'}), 404
    
    return jsonify(scheme.to_dict())

@app.route('/api/reports', methods=['GET', 'POST'])
def handle_reports():
    if request.method == 'POST':
        try:
            verify_jwt_in_request()   # validates token from Authorization header
            current_user_id = get_jwt_identity()
            user_id = int(current_user_id)
        except Exception:
            return jsonify({'error': 'Authentication required'}), 401

        # Support both JSON and multipart/form-data submissions
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Collect text fields from form data
            report_data = {
                'report_type': request.form.get('report_type', ''),
                'title': request.form.get('title', ''),
                'description': request.form.get('description', ''),
                'location': request.form.get('location', ''),
                'city': request.form.get('city', ''),
                'district': request.form.get('district', ''),
                'state': request.form.get('state', ''),
                'data': request.form.get('data', '{}'),
                'latitude': request.form.get('latitude'),
                'longitude': request.form.get('longitude'),
            }

            # Handle optional photo upload
            photo_url = None
            if 'photo' in request.files:
                photo_file = request.files['photo']
                ok, err = validate_image_file(photo_file)
                if not ok:
                    return jsonify({'error': err}), 400
                try:
                    upload_result = upload_report_image(photo_file)
                    photo_url = upload_result['url']
                except Exception as upload_err:
                    return jsonify({'error': f'Image upload failed: {str(upload_err)}'}), 500

        else:
            report_data = request.json or {}

        latitude = _parse_float(report_data.get('latitude'))
        longitude = _parse_float(report_data.get('longitude'))
        if (latitude is None or longitude is None):
            geocode_query = _build_location_query_from_report_payload(report_data)
            if geocode_query:
                geo_result = geocoding_service.geocode(geocode_query, limit=1)
                if geo_result.get('ok') and geo_result.get('results'):
                    best_match = geo_result['results'][0]
                    latitude = best_match.get('latitude')
                    longitude = best_match.get('longitude')

        report_data['latitude'] = latitude
        report_data['longitude'] = longitude

        if request.content_type and 'multipart/form-data' in request.content_type:
            report = citizen_intel.submit_report(user_id, report_data)

            # Attach photo_url to the newly created report
            if photo_url and report:
                report_id = report.get('id')
                if report_id:
                    db_report = db.session.get(CitizenReport, report_id)
                    if db_report:
                        db_report.photo_url = photo_url
                        db_report.image_url = photo_url
                        db.session.commit()
                        report['photo_url'] = photo_url
                        report['image_url'] = photo_url
        else:
            report = citizen_intel.submit_report(user_id, report_data)

        return jsonify({
            'message': 'Report submitted successfully',
            'report': report
        })
    
    else:
        filters = {
            'city': request.args.get('city'),
            'state': request.args.get('state'),
            'district': request.args.get('district'),
            'report_type': request.args.get('type'),
            'verified_only': request.args.get('verified', 'false').lower() == 'true',
            'priority': request.args.get('priority'),
            'status': request.args.get('status'),
            'time_range': int(request.args.get('time_range', 168))
        }
        
        reports = citizen_intel.get_reports(filters)
        
        return jsonify({'reports': reports})


@app.route('/api/government/reports', methods=['GET'])
@jwt_required()
@government_required
def get_government_reports(user):
    """Return citizen reports filtered by authenticated government's jurisdiction."""
    gov_level = (user.gov_level or '').strip().lower()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    per_page = min(per_page, 100)

    query, error_response, error_code = _apply_government_scope(CitizenReport.query, user)
    if error_response is not None:
        return error_response, error_code

    query = _apply_common_report_filters(query)

    query = query.order_by(CitizenReport.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'reports': [report.to_dict() for report in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        },
        'viewing': {
            'gov_level': gov_level,
            'state': user.state,
            'district': user.district,
            'city': user.city,
        }
    })


@app.route('/api/geocode', methods=['POST'])
def geocode_address():
    data = request.get_json(silent=True) or {}
    query = (data.get('query') or '').strip()
    if not query:
        return jsonify({'error': 'query is required'}), 400

    limit = data.get('limit', 5)
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 5

    result = geocoding_service.geocode(query, limit=limit)
    if not result.get('ok'):
        return jsonify({'error': result.get('error', 'Geocoding failed'), 'results': []}), 502

    return jsonify(result)


@app.route('/api/reverse-geocode', methods=['GET'])
def reverse_geocode():
    latitude = _parse_float(request.args.get('latitude'))
    longitude = _parse_float(request.args.get('longitude'))
    if latitude is None or longitude is None:
        return jsonify({'error': 'latitude and longitude query params are required'}), 400

    result = geocoding_service.reverse_geocode(latitude, longitude)
    if not result.get('ok'):
        return jsonify({'error': result.get('error', 'Reverse geocoding failed')}), 502

    return jsonify(result)


@app.route('/api/government/reports/map-data', methods=['GET'])
@jwt_required()
@government_required
def get_government_reports_map_data(user):
    query, error_response, error_code = _apply_government_scope(CitizenReport.query, user)
    if error_response is not None:
        return error_response, error_code

    query = _apply_common_report_filters(query)
    query = query.filter(CitizenReport.latitude.isnot(None), CitizenReport.longitude.isnot(None))

    bbox = parse_bbox(request.args.get('bbox'))
    if bbox:
        min_lon, min_lat, max_lon, max_lat = bbox
        query = query.filter(
            CitizenReport.longitude >= min_lon,
            CitizenReport.longitude <= max_lon,
            CitizenReport.latitude >= min_lat,
            CitizenReport.latitude <= max_lat,
        )

    limit = request.args.get('limit', 1500, type=int)
    if limit is None or limit < 1:
        limit = 1500
    limit = min(limit, 5000)

    reports = query.order_by(CitizenReport.created_at.desc()).limit(limit).all()

    points = []
    category_counter = Counter()
    status_counter = Counter()
    region_counter = Counter()

    for report in reports:
        region_name = report.district or report.city or report.state or 'Unknown'
        category_counter[report.report_type or 'unknown'] += 1
        status_counter[report.status or 'pending'] += 1
        region_counter[region_name] += 1

        points.append({
            'id': report.id,
            'title': report.title or report.report_type or 'Citizen Report',
            'report_type': report.report_type,
            'status': report.status,
            'priority': report.priority,
            'verified': report.verified,
            'state': report.state,
            'district': report.district,
            'city': report.city,
            'location': report.location,
            'latitude': report.latitude,
            'longitude': report.longitude,
            'created_at': report.created_at.isoformat() if report.created_at else None,
            'upvotes': report.upvotes,
        })

    clusters, noise_point_ids = _compute_spatial_clusters(
        points,
        eps_km=request.args.get('cluster_eps_km', 4.0, type=float) or 4.0,
        min_points=request.args.get('cluster_min_points', 3, type=int) or 3,
    )

    region_geojson, ranked_regions = _build_region_overlays(points)

    top_hotspots = [
        {
            'type': 'cluster',
            'cluster_id': row['cluster_id'],
            'count': row['size'],
            'density_per_km2': row['density_per_km2'],
            'region_hint': row['top_category'],
            'center': row['center'],
            'insight': (
                f"Cluster {row['cluster_id']} has {row['size']} incidents "
                f"at {row['density_per_km2']} incidents/km^2"
            ),
        }
        for row in clusters[:3]
    ]

    if len(top_hotspots) < 3:
        fallback_hotspots = [
            {
                'type': 'region',
                'region': row['region'],
                'count': row['count'],
                'density_per_km2': None,
                'insight': f"{row['region']} has {row['count']} incidents in current view",
            }
            for row in ranked_regions[: 3 - len(top_hotspots)]
        ]
        top_hotspots.extend(fallback_hotspots)

    least_active_regions = [
        {'region': row['region'], 'count': row['count']}
        for row in sorted(ranked_regions, key=lambda item: item['count'])[:3]
    ]

    anomalies = _compute_temporal_spikes(points)

    return jsonify({
        'points': points,
        'clusters': clusters,
        'noise_point_ids': noise_point_ids,
        'region_geojson': region_geojson,
        'insights': {
            'total_points': len(points),
            'category_breakdown': dict(category_counter),
            'status_breakdown': dict(status_counter),
            'top_hotspots': top_hotspots,
            'least_active_regions': least_active_regions,
            'anomalies': anomalies,
            'region_rankings': ranked_regions[:10],
            'cluster_summary': {
                'count': len(clusters),
                'largest_cluster_size': max([row['size'] for row in clusters], default=0),
                'noise_points': len(noise_point_ids),
            },
        },
    })


@app.route('/api/government/reports/geo/nearby', methods=['GET'])
@jwt_required()
@government_required
def get_government_reports_nearby(user):
    latitude = _parse_float(request.args.get('latitude'))
    longitude = _parse_float(request.args.get('longitude'))
    if latitude is None or longitude is None:
        return jsonify({'error': 'latitude and longitude are required'}), 400

    radius_km = request.args.get('radius_km', 10, type=float)
    if radius_km is None or radius_km <= 0:
        radius_km = 10.0
    radius_km = min(radius_km, 1000.0)

    limit = request.args.get('limit', 200, type=int)
    if limit is None or limit < 1:
        limit = 200
    limit = min(limit, 1000)

    if db.engine.dialect.name == 'postgresql':
        try:
            params = {
                'lon': longitude,
                'lat': latitude,
                'radius_m': radius_km * 1000,
                'limit': limit,
            }
            sql = text("""
                SELECT
                    cr.id,
                    cr.title,
                    cr.report_type,
                    cr.status,
                    cr.priority,
                    cr.verified,
                    cr.state,
                    cr.district,
                    cr.city,
                    cr.location,
                    cr.latitude,
                    cr.longitude,
                    cr.created_at,
                    ST_DistanceSphere(
                        cr.geom,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                    ) / 1000.0 AS distance_km
                FROM citizen_report cr
                WHERE cr.geom IS NOT NULL
                  AND ST_DWithin(
                        cr.geom::geography,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                        :radius_m
                  )
                ORDER BY distance_km ASC
                LIMIT :limit
            """)

            rows = db.session.execute(sql, params).mappings().all()
            return jsonify({
                'center': {'latitude': latitude, 'longitude': longitude},
                'radius_km': radius_km,
                'reports': [
                    {
                        'id': row['id'],
                        'title': row['title'],
                        'report_type': row['report_type'],
                        'status': row['status'],
                        'priority': row['priority'],
                        'verified': row['verified'],
                        'state': row['state'],
                        'district': row['district'],
                        'city': row['city'],
                        'location': row['location'],
                        'latitude': row['latitude'],
                        'longitude': row['longitude'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'distance_km': round(float(row['distance_km']), 3),
                    }
                    for row in rows
                ],
            })
        except Exception:
            # Graceful fallback below for non-PostGIS cases.
            pass

    query, error_response, error_code = _apply_government_scope(CitizenReport.query, user)
    if error_response is not None:
        return error_response, error_code

    query = _apply_common_report_filters(query)
    query = query.filter(CitizenReport.latitude.isnot(None), CitizenReport.longitude.isnot(None))

    # Bounding box pre-filter reduces candidate set before Haversine calculation.
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / max(1e-6, (111.0 * abs(math.cos(math.radians(latitude)))))
    query = query.filter(
        CitizenReport.latitude >= latitude - delta_lat,
        CitizenReport.latitude <= latitude + delta_lat,
        CitizenReport.longitude >= longitude - delta_lon,
        CitizenReport.longitude <= longitude + delta_lon,
    )

    results = []
    for report in query.order_by(CitizenReport.created_at.desc()).limit(5000).all():
        distance = haversine_km(latitude, longitude, report.latitude, report.longitude)
        if distance <= radius_km:
            results.append({
                'id': report.id,
                'title': report.title,
                'report_type': report.report_type,
                'status': report.status,
                'priority': report.priority,
                'verified': report.verified,
                'state': report.state,
                'district': report.district,
                'city': report.city,
                'location': report.location,
                'latitude': report.latitude,
                'longitude': report.longitude,
                'created_at': report.created_at.isoformat() if report.created_at else None,
                'distance_km': round(distance, 3),
            })

    results.sort(key=lambda row: row['distance_km'])
    return jsonify({
        'center': {'latitude': latitude, 'longitude': longitude},
        'radius_km': radius_km,
        'reports': results[:limit],
    })


@app.route('/api/government/reports/geo/analytics', methods=['GET'])
@jwt_required()
@government_required
def get_government_reports_geo_analytics(user):
    group_by = (request.args.get('group_by') or 'region').strip().lower()
    if group_by not in {'state', 'district', 'city', 'type', 'status', 'region'}:
        return jsonify({'error': 'group_by must be one of: state, district, city, type, status, region'}), 400

    query, error_response, error_code = _apply_government_scope(CitizenReport.query, user)
    if error_response is not None:
        return error_response, error_code

    query = _apply_common_report_filters(query)
    reports = query.all()

    buckets = Counter()
    for report in reports:
        if group_by == 'state':
            key = report.state or 'Unknown'
        elif group_by == 'district':
            key = report.district or 'Unknown'
        elif group_by == 'city':
            key = report.city or 'Unknown'
        elif group_by == 'type':
            key = report.report_type or 'Unknown'
        elif group_by == 'status':
            key = report.status or 'Unknown'
        else:
            key = report.district or report.city or report.state or 'Unknown'
        buckets[key] += 1

    ranked = [
        {'group': key, 'count': value}
        for key, value in buckets.most_common(50)
    ]

    return jsonify({
        'group_by': group_by,
        'total_reports': len(reports),
        'groups': ranked,
    })

@app.route('/api/reports/<int:report_id>/upload-photo', methods=['POST'])
@jwt_required()
def upload_report_photo(report_id):
    """Upload or replace the photo attached to an existing report.

    Expects multipart/form-data with a 'photo' field.
    Only the report owner or a gov/admin user may update the photo.
    """
    current_user_id = get_jwt_identity()

    report = db.session.get(CitizenReport, report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    # Authorisation: only the owner or privileged roles
    requesting_user = db.session.get(User, int(current_user_id))
    if not requesting_user:
        return jsonify({'error': 'User not found'}), 404

    if report.user_id != int(current_user_id) and _normalized_role(requesting_user) not in ('government', 'admin'):
        return jsonify({'error': 'Forbidden'}), 403

    if 'photo' not in request.files:
        return jsonify({'error': 'No photo file provided'}), 400

    photo_file = request.files['photo']
    ok, err = validate_image_file(photo_file)
    if not ok:
        return jsonify({'error': err}), 400

    try:
        upload_result = upload_report_image(photo_file, report_id=report_id)
    except Exception as e:
        return jsonify({'error': f'Image upload failed: {str(e)}'}), 500

    report.photo_url = upload_result['url']
    report.image_url = upload_result['url']
    db.session.commit()

    return jsonify({
        'message': 'Photo uploaded successfully',
        'photo_url': upload_result['url'],
        'image_url': upload_result['url'],
        'report_id': report_id,
    })


@app.route('/api/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report_detail(report_id):
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, int(current_user_id))
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    report = db.session.get(CitizenReport, report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    current_role = _normalized_role(current_user)

    if current_role == 'government':
        if not _in_user_scope(current_user, report):
            return jsonify({'error': 'Forbidden'}), 403
    elif current_role != 'admin' and report.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403

    can_assign = False
    can_update_status = False
    if current_role == 'government' and _in_user_scope(current_user, report):
        can_assign = True
        if report.assigned_to == current_user.id:
            can_update_status = True
        elif report.assigned_user and _is_higher_authority(current_user, report.assigned_user) and _same_jurisdiction_for_control(current_user, report.assigned_user):
            can_update_status = True
        elif report.assigned_to is None:
            can_update_status = True
    elif current_role == 'admin':
        can_assign = True
        can_update_status = True

    audit_logs = [log.to_dict() for log in sorted(report.audit_logs, key=lambda x: x.created_at, reverse=True)[:20]]

    return jsonify({
        'report': _serialize_report_detail(report),
        'permissions': {
            'can_assign': can_assign,
            'can_update_status': can_update_status,
        },
        'audit_logs': audit_logs,
    })


@app.route('/api/government/reports/<int:report_id>/eligible-assignees', methods=['GET'])
@jwt_required()
@government_required
def get_eligible_assignees(current_user, report_id):
    report = db.session.get(CitizenReport, report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    if not _in_user_scope(current_user, report):
        return jsonify({'error': 'Forbidden'}), 403

    candidates = User.query.filter(User.role.in_(['government', 'gov'])).all()
    eligible = []
    for user in candidates:
        if not user.gov_level:
            continue
        if not _is_same_or_lower_authority(current_user, user):
            continue
        if not _within_assigner_jurisdiction(current_user, user):
            continue
        if not _in_user_scope(user, report):
            continue

        eligible.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'gov_level': user.gov_level,
            'state': user.state,
            'district': user.district,
            'city': user.city,
        })

    return jsonify({'users': eligible})


@app.route('/api/government/reports/<int:report_id>/assign', methods=['POST'])
@jwt_required()
@government_required
def assign_report(current_user, report_id):
    report = db.session.get(CitizenReport, report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    if not _in_user_scope(current_user, report):
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json(silent=True) or {}
    assignee_id = data.get('assigned_to') or data.get('assigned_to_user_id')
    requested_status = (data.get('status') or '').strip().lower() or None

    if not assignee_id:
        return jsonify({'error': 'assigned_to is required'}), 400

    assignee = db.session.get(User, int(assignee_id))
    if not assignee:
        return jsonify({'error': 'Assignee user not found'}), 404
    if _normalized_role(assignee) != 'government':
        return jsonify({'error': 'Assignee must be a government user'}), 400

    if not _is_same_or_lower_authority(current_user, assignee):
        return jsonify({'error': 'Cannot assign to higher authority'}), 403
    if not _within_assigner_jurisdiction(current_user, assignee):
        return jsonify({'error': 'Cannot assign outside your jurisdiction'}), 403
    if not _in_user_scope(assignee, report):
        return jsonify({'error': 'Assignee does not have jurisdiction for this report'}), 403

    previous_assignee = report.assigned_to
    report.assigned_to = assignee.id
    report.assigned_by = current_user.id

    log = ReportAuditLog(
        report_id=report.id,
        actor_user_id=current_user.id,
        action='assigned',
        from_assigned_to=previous_assignee,
        to_assigned_to=assignee.id,
        notes='Report assignment updated',
    )
    db.session.add(log)

    if requested_status:
        if requested_status not in VALID_REPORT_STATUSES:
            return jsonify({'error': 'Invalid status. Allowed: pending, working, completed'}), 400

        current_status = (report.status or 'pending').lower()
        if requested_status != current_status and requested_status not in STATUS_TRANSITIONS.get(current_status, set()):
            return jsonify({'error': f'Invalid status transition: {current_status} -> {requested_status}'}), 400

        if requested_status != current_status:
            status_log = ReportAuditLog(
                report_id=report.id,
                actor_user_id=current_user.id,
                action='status_changed',
                from_status=current_status,
                to_status=requested_status,
                notes='Status updated during assignment',
            )
            db.session.add(status_log)
            report.status = requested_status

    db.session.commit()

    return jsonify({
        'message': 'Report assigned successfully',
        'report': _serialize_report_detail(report),
    })


@app.route('/api/government/reports/<int:report_id>/status', methods=['POST'])
@jwt_required()
def update_report_status(report_id):
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, int(current_user_id))
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    if _normalized_role(current_user) != 'government':
        return jsonify({'error': 'Forbidden. Government role required.'}), 403

    report = db.session.get(CitizenReport, report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    if not _in_user_scope(current_user, report):
        return jsonify({'error': 'Forbidden'}), 403

    allowed = False
    if report.assigned_to == current_user.id:
        allowed = True
    elif report.assigned_user and _is_higher_authority(current_user, report.assigned_user) and _same_jurisdiction_for_control(current_user, report.assigned_user):
        allowed = True
    elif report.assigned_to is None:
        allowed = True

    if not allowed:
        return jsonify({'error': 'Forbidden. Only assignee or higher authority can update status.'}), 403

    data = request.get_json(silent=True) or {}
    new_status = (data.get('status') or '').strip().lower()
    if new_status not in VALID_REPORT_STATUSES:
        return jsonify({'error': 'Invalid status. Allowed: pending, working, completed'}), 400

    current_status = (report.status or 'pending').lower()
    if new_status == current_status:
        return jsonify({'message': 'Status unchanged', 'report': _serialize_report_detail(report)})

    allowed_next = STATUS_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next:
        return jsonify({'error': f'Invalid status transition: {current_status} -> {new_status}'}), 400

    report.status = new_status
    log = ReportAuditLog(
        report_id=report.id,
        actor_user_id=current_user.id,
        action='status_changed',
        from_status=current_status,
        to_status=new_status,
        notes='Workflow status updated',
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'message': 'Status updated successfully',
        'report': _serialize_report_detail(report),
    })


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

    def _build_query():
        q = Prediction.query.filter_by(status=status)
        if city:
            q = q.filter_by(city=city)
        elif state:
            q = q.filter_by(state=state)
        if category:
            q = q.filter_by(category=category)
        return q

    query = _build_query()

    predictions = query.order_by(Prediction.confidence.desc()).all()

    # If no active predictions exist, opportunistically generate from recent fetched articles.
    if status == 'active' and not predictions:
        try:
            crisis_predictor.analyze_trends()
            predictions = _build_query().order_by(Prediction.confidence.desc()).all()
        except Exception as e:
            app.logger.warning(f"Prediction auto-generation skipped: {e}")
    
    return jsonify({
        'predictions': [p.to_dict() for p in predictions]
    })

@app.route('/api/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction_detail(prediction_id):
    prediction = db.session.get(Prediction, prediction_id)
    
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


@app.route('/query', methods=['POST'])
def graph_query_alias():
    """Alias endpoint requested by graph reasoning API contract."""
    data = request.get_json(silent=True) or {}
    nl_query = data.get('query', '')
    max_depth = int(data.get('max_depth', 4))
    result = graph_reasoner.interpret_and_query(nl_query, max_depth=max_depth)
    status = 400 if result.get('error') else 200
    return jsonify(result), status


@app.route('/api/graph/query', methods=['POST'])
def graph_query():
    data = request.get_json(silent=True) or {}
    nl_query = data.get('query', '')
    max_depth = int(data.get('max_depth', 4))
    result = graph_reasoner.interpret_and_query(nl_query, max_depth=max_depth)
    status = 400 if result.get('error') else 200
    return jsonify(result), status


@app.route('/api/graph/schema', methods=['GET'])
def graph_schema():
    return jsonify(graph_reasoner.get_schema())


@app.route('/api/graph/validate-query', methods=['POST'])
def graph_validate_query():
    data = request.get_json(silent=True) or {}
    nl_query = data.get('query', '')
    max_depth = int(data.get('max_depth', 4))

    graph_data = graph_reasoner._build_graph()  # internal preflight snapshot
    intent = graph_reasoner.parse_intent(nl_query, max_depth=max_depth)
    validation = graph_reasoner.validate_intent(graph_data, intent)

    return jsonify({
        'intent': intent.__dict__,
        'validation': validation,
        'integrity_issues': graph_data.get('integrity_issues', [])[:25],
    })


@app.route('/api/graph/path', methods=['GET'])
def graph_path():
    source = request.args.get('source', '')
    target = request.args.get('target', '')
    max_depth = request.args.get('max_depth', 5, type=int)
    result = graph_reasoner.shortest_path(source, target, max_depth=max_depth)
    status = 400 if result.get('error') else 200
    return jsonify(result), status


@app.route('/api/graph/neighbors', methods=['GET'])
def graph_neighbors():
    entity = request.args.get('entity', '')
    depth = request.args.get('depth', 1, type=int)
    direction = request.args.get('direction', 'both')
    limit_nodes = request.args.get('limit_nodes', 250, type=int)
    result = graph_reasoner.neighbors(
        entity_name=entity,
        depth=max(1, min(depth, 6)),
        direction=direction if direction in {'in', 'out', 'both'} else 'both',
        limit_nodes=max(50, min(limit_nodes, 300)),
    )
    status = 400 if result.get('error') else 200
    return jsonify(result), status


@app.route('/api/graph/dfs', methods=['GET'])
def graph_dfs():
    source = request.args.get('source', '')
    depth = request.args.get('depth', 3, type=int)
    limit_paths = request.args.get('limit_paths', 20, type=int)
    result = graph_reasoner.dfs_explore(
        source_name=source,
        max_depth=max(1, min(depth, 6)),
        limit_paths=max(1, min(limit_paths, 50)),
    )
    status = 400 if result.get('error') else 200
    return jsonify(result), status


@app.route('/api/graph/search', methods=['GET'])
def graph_search():
    q = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        'matches': graph_reasoner.search_entities(q, limit=max(1, min(limit, 25)))
    })


@app.route('/api/graph/subgraph', methods=['GET'])
def graph_subgraph():
    limit_nodes = request.args.get('limit_nodes', 120, type=int)
    limit_edges = request.args.get('limit_edges', 240, type=int)
    result = graph_reasoner.get_seed_subgraph(
        limit_nodes=max(20, min(limit_nodes, 300)),
        limit_edges=max(40, min(limit_edges, 600)),
    )
    return jsonify(result)

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
    # Keep backward-compatible route while returning visualization-friendly IDs.
    return jsonify(graph_reasoner.get_seed_subgraph(limit_nodes=120, limit_edges=240))

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