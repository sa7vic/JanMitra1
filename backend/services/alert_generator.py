from models.database import db, User, Prediction, UserAlert, CitizenReport
from datetime import datetime, timedelta
import json

class AlertGenerator:
    def __init__(self):
        pass
    
    def generate_alerts_for_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return []
        
        alerts = []
        
        location_alerts = self._generate_location_alerts(user)
        alerts.extend(location_alerts)
        
        occupation_alerts = self._generate_occupation_alerts(user)
        alerts.extend(occupation_alerts)
        
        health_alerts = self._generate_health_alerts(user)
        alerts.extend(health_alerts)
        
        for alert_data in alerts:
            existing = UserAlert.query.filter_by(
                user_id=user_id,
                prediction_id=alert_data.get('prediction_id'),
                dismissed=False
            ).first()
            
            if not existing:
                alert = UserAlert(
                    user_id=user_id,
                    **alert_data
                )
                db.session.add(alert)
        
        db.session.commit()
        return alerts
    
    def _generate_location_alerts(self, user):
        alerts = []
        
        predictions = Prediction.query.filter_by(status='active').all()
        
        for pred in predictions:
            if self._is_relevant_location(user, pred):
                severity_messages = {
                    'high': f'⚠️ HIGH ALERT: {pred.title}',
                    'medium': f'⚡ ALERT: {pred.title}',
                    'low': f'ℹ️ Advisory: {pred.title}'
                }
                
                days_ahead = (pred.predicted_date - datetime.utcnow()).days if pred.predicted_date else 7
                
                alert_data = {
                    'prediction_id': pred.id,
                    'alert_type': 'location_based',
                    'title': severity_messages.get(pred.severity, pred.title),
                    'message': self._create_alert_message(pred, user, days_ahead),
                    'severity': pred.severity,
                    'actionable': True
                }
                alerts.append(alert_data)
        
        return alerts
    
    def _generate_occupation_alerts(self, user):
        alerts = []
        
        if not user.occupation:
            return alerts
        
        predictions = Prediction.query.filter_by(status='active').all()
        
        occupation_categories = {
            'farmer': ['agriculture', 'weather', 'commodity'],
            'business': ['economy', 'commodity'],
            'student': ['education', 'health'],
            'driver': ['economy', 'transport']
        }
        
        user_occ = user.occupation.lower()
        relevant_categories = []
        
        for occ_key, categories in occupation_categories.items():
            if occ_key in user_occ:
                relevant_categories.extend(categories)
        
        for pred in predictions:
            if pred.category in relevant_categories:
                alert_data = {
                    'prediction_id': pred.id,
                    'alert_type': 'occupation_based',
                    'title': f'📊 Affects your {user.occupation}: {pred.title}',
                    'message': self._create_occupation_message(pred, user),
                    'severity': pred.severity,
                    'actionable': True
                }
                alerts.append(alert_data)
        
        return alerts
    
    def _generate_health_alerts(self, user):
        alerts = []
        
        health_predictions = Prediction.query.filter_by(
            category='health',
            status='active'
        ).all()
        
        for pred in health_predictions:
            if self._is_relevant_location(user, pred):
                if user.family_size and user.family_size > 2:
                    message_suffix = f" Your family of {user.family_size} members is at risk."
                else:
                    message_suffix = " Take necessary precautions."
                
                alert_data = {
                    'prediction_id': pred.id,
                    'alert_type': 'health',
                    'title': f'🏥 Health Alert: {pred.title}',
                    'message': pred.description + message_suffix,
                    'severity': pred.severity,
                    'actionable': True
                }
                alerts.append(alert_data)
        
        return alerts
    
    def _is_relevant_location(self, user, prediction):
        if not prediction.location or prediction.location.lower() == 'national':
            return True
        
        if user.city and prediction.city:
            if user.city.lower() == prediction.city.lower():
                return True
        
        if user.state and prediction.state:
            if user.state.lower() == prediction.state.lower():
                return True
        
        if user.location and prediction.location:
            if prediction.location.lower() in user.location.lower():
                return True
        
        return False
    
    def _create_alert_message(self, prediction, user, days_ahead):
        base_message = prediction.description
        
        timeline = f"\n\n⏰ Expected in: {days_ahead} days"
        
        confidence = f"\n📊 Confidence: {int(prediction.confidence * 100)}%"
        
        location = f"\n📍 Location: {prediction.location}"
        
        actions = self._get_recommended_actions(prediction, user)
        
        message = base_message + timeline + confidence + location + actions
        
        return message
    
    def _create_occupation_message(self, prediction, user):
        occupation_impacts = {
            'farmer': {
                'agriculture': 'This will affect crop yields and farming income.',
                'weather': 'Plan your sowing/harvesting accordingly.',
                'commodity': 'Input costs may be impacted.'
            },
            'business': {
                'economy': 'This may impact your business operations and costs.',
                'commodity': 'Your inventory and pricing strategy may need adjustment.'
            }
        }
        
        base = prediction.description
        
        user_occ = user.occupation.lower()
        for occ_key, impacts in occupation_impacts.items():
            if occ_key in user_occ and prediction.category in impacts:
                base += f"\n\n💼 Impact on you: {impacts[prediction.category]}"
        
        return base
    
    def _get_recommended_actions(self, prediction, user):
        actions = "\n\n✅ What you should do:"
        
        if prediction.category == 'health':
            actions += "\n• Get tested at nearest health center"
            actions += "\n• Take preventive measures"
            actions += "\n• Keep emergency medicines ready"
        elif prediction.category == 'weather':
            actions += "\n• Stay updated with weather alerts"
            actions += "\n• Keep emergency supplies ready"
            actions += "\n• Follow evacuation instructions if any"
        elif prediction.category == 'economy':
            actions += "\n• Budget accordingly for price changes"
            actions += "\n• Stock essential items if needed"
            actions += "\n• Explore alternatives"
        elif prediction.category == 'agriculture':
            if user.occupation and 'farm' in user.occupation.lower():
                actions += "\n• Consult local agriculture officer"
                actions += "\n• Check crop insurance status"
                actions += "\n• Plan alternative strategies"
        
        return actions
    
    def get_user_alerts(self, user_id, include_read=False):
        query = UserAlert.query.filter_by(user_id=user_id, dismissed=False)
        
        if not include_read:
            query = query.filter_by(read=False)
        
        alerts = query.order_by(UserAlert.created_at.desc()).all()
        
        return [alert.to_dict() for alert in alerts]
    
    def mark_alert_read(self, alert_id, user_id):
        alert = UserAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.read = True
            db.session.commit()
            return True
        return False
    
    def dismiss_alert(self, alert_id, user_id):
        alert = UserAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.dismissed = True
            db.session.commit()
            return True
        return False
    
    def mark_action_taken(self, alert_id, user_id):
        alert = UserAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.action_taken = True
            db.session.commit()
            return True
        return False