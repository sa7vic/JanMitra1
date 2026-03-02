from models.database import db, CitizenReport, User
from datetime import datetime, timedelta
import json

class CitizenIntel:
    def __init__(self):
        pass
    
    def submit_report(self, user_id, report_data):
        user = User.query.get(user_id)
        if not user:
            return None
        
        report = CitizenReport(
            user_id=user_id,
            report_type=report_data.get('report_type'),
            title=report_data.get('title'),
            description=report_data.get('description'),
            data=json.dumps(report_data.get('data', {})),
            location=report_data.get('location') or user.location,
            state=report_data.get('state') or user.state,
            city=report_data.get('city') or user.city,
            latitude=report_data.get('latitude'),
            longitude=report_data.get('longitude'),
            photo_url=report_data.get('photo_url')
        )
        
        db.session.add(report)
        db.session.commit()
        
        self._auto_verify_report(report)
        
        self._update_user_reputation(user_id, 5)
        
        return report.to_dict()
    
    def _auto_verify_report(self, report):
        time_window = datetime.utcnow() - timedelta(hours=48)
        
        similar_reports = CitizenReport.query.filter(
            CitizenReport.report_type == report.report_type,
            CitizenReport.city == report.city,
            CitizenReport.created_at >= time_window,
            CitizenReport.id != report.id
        ).all()
        
        if len(similar_reports) >= 3:
            report.verified = True
            report.verification_confidence = min(0.9, 0.5 + (len(similar_reports) * 0.1))
            report.priority = 'high'
            
            for similar in similar_reports:
                if not similar.verified:
                    similar.verified = True
                    similar.verification_confidence = report.verification_confidence
                    self._update_user_reputation(similar.user_id, 10)
            
            db.session.commit()
    
    def _update_user_reputation(self, user_id, points):
        user = User.query.get(user_id)
        if user:
            user.reputation_score = (user.reputation_score or 0) + points
            db.session.commit()
    
    def upvote_report(self, report_id, user_id):
        report = CitizenReport.query.get(report_id)
        if not report:
            return None
        
        report.upvotes += 1
        
        if report.upvotes >= 5 and not report.verified:
            report.verified = True
            report.verification_confidence = 0.7
        
        if report.upvotes >= 10:
            report.priority = 'high'
        
        self._update_user_reputation(report.user_id, 2)
        
        db.session.commit()
        
        return report.to_dict()
    
    def downvote_report(self, report_id, user_id):
        report = CitizenReport.query.get(report_id)
        if not report:
            return None
        
        report.downvotes += 1
        
        if report.downvotes >= 5 and report.verified:
            report.verified = False
            report.verification_confidence = 0.3
        
        db.session.commit()
        
        return report.to_dict()
    
    def get_reports(self, filters=None):
        query = CitizenReport.query
        
        if filters:
            if filters.get('city'):
                query = query.filter_by(city=filters['city'])
            
            if filters.get('state'):
                query = query.filter_by(state=filters['state'])
            
            if filters.get('report_type'):
                query = query.filter_by(report_type=filters['report_type'])
            
            if filters.get('verified_only'):
                query = query.filter_by(verified=True)
            
            if filters.get('priority'):
                query = query.filter_by(priority=filters['priority'])
            
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            
            if filters.get('time_range'):
                hours = filters['time_range']
                time_limit = datetime.utcnow() - timedelta(hours=hours)
                query = query.filter(CitizenReport.created_at >= time_limit)
        
        reports = query.order_by(CitizenReport.created_at.desc()).limit(100).all()
        
        return [r.to_dict() for r in reports]
    
    def get_trending_issues(self, city=None, state=None, limit=10):
        time_window = datetime.utcnow() - timedelta(hours=24)
        
        query = CitizenReport.query.filter(
            CitizenReport.created_at >= time_window
        )
        
        if city:
            query = query.filter_by(city=city)
        elif state:
            query = query.filter_by(state=state)
        
        reports = query.all()
        
        issue_counts = {}
        for report in reports:
            key = f"{report.report_type}_{report.title}"
            if key not in issue_counts:
                issue_counts[key] = {
                    'report_type': report.report_type,
                    'title': report.title,
                    'count': 0,
                    'verified_count': 0,
                    'location': report.city or report.state,
                    'priority': report.priority,
                    'sample_report': report.to_dict()
                }
            issue_counts[key]['count'] += 1
            if report.verified:
                issue_counts[key]['verified_count'] += 1
        
        trending = sorted(issue_counts.values(), key=lambda x: x['count'], reverse=True)
        
        return trending[:limit]
    
    def get_aggregated_prices(self, city=None, state=None, item=None):
        time_window = datetime.utcnow() - timedelta(days=7)
        
        query = CitizenReport.query.filter(
            CitizenReport.report_type == 'price',
            CitizenReport.created_at >= time_window
        )
        
        if city:
            query = query.filter_by(city=city)
        elif state:
            query = query.filter_by(state=state)
        
        reports = query.all()
        
        prices = {}
        for report in reports:
            data = json.loads(report.data) if report.data else {}
            item_name = data.get('item', '').lower()
            price = data.get('price')
            
            if not item_name or not price:
                continue
            
            if item and item.lower() != item_name:
                continue
            
            if item_name not in prices:
                prices[item_name] = {
                    'item': item_name,
                    'prices': [],
                    'locations': [],
                    'reports_count': 0
                }
            
            prices[item_name]['prices'].append(float(price))
            prices[item_name]['locations'].append(report.city or report.state)
            prices[item_name]['reports_count'] += 1
        
        aggregated = {}
        for item_name, data in prices.items():
            price_list = data['prices']
            aggregated[item_name] = {
                'item': item_name,
                'average': sum(price_list) / len(price_list),
                'min': min(price_list),
                'max': max(price_list),
                'reports': data['reports_count'],
                'locations': list(set(data['locations'])),
                'last_updated': datetime.utcnow().isoformat()
            }
        
        return aggregated
    
    def update_report_status(self, report_id, status, notes=None):
        report = CitizenReport.query.get(report_id)
        if not report:
            return None
        
        report.status = status
        
        if status == 'resolved':
            self._update_user_reputation(report.user_id, 15)
        
        db.session.commit()
        
        return report.to_dict()
    
    def get_user_reports(self, user_id):
        reports = CitizenReport.query.filter_by(user_id=user_id).order_by(
            CitizenReport.created_at.desc()
        ).all()
        
        return [r.to_dict() for r in reports]
    
    def get_stats(self, city=None, state=None):
        query = CitizenReport.query
        
        if city:
            query = query.filter_by(city=city)
        elif state:
            query = query.filter_by(state=state)
        
        total_reports = query.count()
        verified_reports = query.filter_by(verified=True).count()
        
        time_window = datetime.utcnow() - timedelta(hours=24)
        recent_reports = query.filter(CitizenReport.created_at >= time_window).count()
        
        resolved_reports = query.filter_by(status='resolved').count()
        
        return {
            'total_reports': total_reports,
            'verified_reports': verified_reports,
            'recent_reports_24h': recent_reports,
            'resolved_reports': resolved_reports,
            'verification_rate': (verified_reports / total_reports * 100) if total_reports > 0 else 0
        }