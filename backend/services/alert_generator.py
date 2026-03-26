import json
from datetime import datetime, timedelta

from models.database import Prediction, User, UserAlert, db


class AlertGenerator:
    def __init__(self):
        self.economic_categories = {
            "economy",
            "commodity",
            "inflation",
            "macro",
        }

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
                prediction_id=alert_data.get("prediction_id"),
                dismissed=False,
            ).first()

            if not existing:
                alert = UserAlert(user_id=user_id, **alert_data)
                db.session.add(alert)

        db.session.commit()
        return alerts

    def _generate_location_alerts(self, user):
        alerts = []

        predictions = Prediction.query.filter_by(status="active").all()

        for pred in predictions:
            if self._is_relevant_location(user, pred):
                if not self._is_alert_data_sufficient(pred):
                    continue

                severity_messages = {
                    "high": f"⚠️ HIGH ALERT: {pred.title}",
                    "medium": f"⚡ ALERT: {pred.title}",
                    "low": f"ℹ️ Advisory: {pred.title}",
                }

                alert_data = {
                    "prediction_id": pred.id,
                    "alert_type": self._resolve_alert_type(
                        pred,
                        "location_based",
                    ),
                    "title": severity_messages.get(pred.severity, pred.title),
                    "message": self._create_alert_message(pred, user),
                    "severity": pred.severity,
                    "actionable": True,
                }
                alerts.append(alert_data)

        return alerts

    def _generate_occupation_alerts(self, user):
        alerts = []

        if not user.occupation:
            return alerts

        predictions = Prediction.query.filter_by(status="active").all()

        occupation_categories = {
            "farmer": ["agriculture", "weather", "commodity"],
            "business": ["economy", "commodity"],
            "student": ["education", "health"],
            "driver": ["economy", "transport"],
        }

        user_occ = user.occupation.lower()
        relevant_categories = []

        for occ_key, categories in occupation_categories.items():
            if occ_key in user_occ:
                relevant_categories.extend(categories)

        for pred in predictions:
            if pred.category in relevant_categories:
                if not self._is_alert_data_sufficient(pred):
                    continue

                alert_data = {
                    "prediction_id": pred.id,
                    "alert_type": self._resolve_alert_type(
                        pred,
                        "occupation_based",
                    ),
                    "title": f"📊 Affects your {user.occupation}: {pred.title}",
                    "message": self._create_occupation_message(pred, user),
                    "severity": pred.severity,
                    "actionable": True,
                }
                alerts.append(alert_data)

        return alerts

    def _generate_health_alerts(self, user):
        alerts = []

        health_predictions = Prediction.query.filter_by(
            category="health",
            status="active",
        ).all()

        for pred in health_predictions:
            if self._is_relevant_location(user, pred):
                if not self._is_alert_data_sufficient(pred):
                    continue

                if user.family_size and user.family_size > 2:
                    message_suffix = (
                        f" Your family of {user.family_size} "
                        "members is at risk."
                    )
                else:
                    message_suffix = " Take necessary precautions."

                alert_data = {
                    "prediction_id": pred.id,
                    "alert_type": self._resolve_alert_type(pred, "health"),
                    "title": f"🏥 Health Alert: {pred.title}",
                    "message": (
                        self._create_alert_message(pred, user) + message_suffix
                    ),
                    "severity": pred.severity,
                    "actionable": True,
                }
                alerts.append(alert_data)

        return alerts

    def _is_relevant_location(self, user, prediction):
        if (
            not prediction.location
            or prediction.location.lower() == "national"
        ):
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

    def _create_alert_message(self, prediction, user):
        evidence = self._parse_evidence(prediction)

        freshness_display = self._format_freshness(
            evidence.get("data_freshness")
        )
        trigger_reason = (
            evidence.get("trigger_reason")
            or prediction.description
            or "Threshold breach detected in recent signals."
        )
        supporting = evidence.get("supporting_indicators") or [
            prediction.category or "Unknown indicator"
        ]
        confidence_label = (
            evidence.get("confidence_label")
            or self._confidence_label_from_score(prediction.confidence)
        )
        confidence_basis = evidence.get(
            "confidence_basis",
            "based on data quality and corroboration",
        )

        lines = [
            f"🧠 Signal Type: {evidence.get('signal_type', 'Mixed')}",
            f"📊 Data Freshness: {freshness_display}",
            f"⚡ Trigger Reason: {trigger_reason}",
            f"📉 Supporting Indicators: {', '.join(supporting)}",
            f"🎯 Confidence: {confidence_label} ({confidence_basis})",
        ]

        model = evidence.get("model") or {}
        model_type = model.get("type")
        uncertainty = model.get("uncertainty")
        assumptions = model.get("assumptions")

        if model_type:
            lines.append(f"🧪 Model: {model_type}")
        if uncertainty:
            lines.append(f"📌 Uncertainty: {uncertainty}")
        if assumptions:
            lines.append(f"🧾 Assumptions: {'; '.join(assumptions)}")

        lines.append(f"📍 Location: {prediction.location}")
        lines.append(self._get_recommended_actions(prediction, user))

        return "\n".join(lines)

    def _create_occupation_message(self, prediction, user):
        base = self._create_alert_message(prediction, user)

        occupation_impacts = {
            "farmer": {
                "agriculture": (
                    "This will affect crop yields and farming income."
                ),
                "weather": "Plan your sowing/harvesting accordingly.",
                "commodity": "Input costs may be impacted.",
            },
            "business": {
                "economy": (
                    "This may impact your business operations and costs."
                ),
                "commodity": (
                    "Your inventory and pricing strategy may need adjustment."
                ),
            },
        }

        user_occ = user.occupation.lower()
        for occ_key, impacts in occupation_impacts.items():
            if occ_key in user_occ and prediction.category in impacts:
                base += f"\n\n💼 Impact on you: {impacts[prediction.category]}"

        return base

    def _get_recommended_actions(self, prediction, user):
        actions = "\n\n✅ What you should do:"

        if prediction.category == "health":
            actions += "\n• Get tested at nearest health center"
            actions += "\n• Take preventive measures"
            actions += "\n• Keep emergency medicines ready"
        elif prediction.category == "weather":
            actions += "\n• Stay updated with weather alerts"
            actions += "\n• Keep emergency supplies ready"
            actions += "\n• Follow evacuation instructions if any"
        elif prediction.category == "economy":
            actions += "\n• Budget accordingly for price changes"
            actions += "\n• Stock essential items if needed"
            actions += "\n• Explore alternatives"
        elif prediction.category == "agriculture":
            if user.occupation and "farm" in user.occupation.lower():
                actions += "\n• Consult local agriculture officer"
                actions += "\n• Check crop insurance status"
                actions += "\n• Plan alternative strategies"

        return actions

    def _resolve_alert_type(self, prediction, fallback_type):
        category = (prediction.category or "").lower()
        if category in self.economic_categories:
            return "realtime_economic"
        return fallback_type

    def _is_alert_data_sufficient(self, prediction):
        category = (prediction.category or "").lower()
        evidence = self._parse_evidence(prediction)

        if category in self.economic_categories:
            required_fields = [
                "signal_type",
                "data_freshness",
                "trigger_reason",
                "supporting_indicators",
            ]
            if any(not evidence.get(field) for field in required_fields):
                return False

            freshness = self._parse_iso_datetime(
                evidence.get("data_freshness")
            )
            if not freshness:
                return False

            signal_type = evidence.get("signal_type", "Mixed").lower()
            max_hours = 24 * 45 if signal_type == "lagging" else 72
            if datetime.utcnow() - freshness > timedelta(hours=max_hours):
                return False

            return True

        # Non-economic alerts still require recent generation.
        is_old = (
            prediction.created_at
            and datetime.utcnow() - prediction.created_at > timedelta(days=7)
        )
        if is_old:
            return False

        return True

    def _parse_evidence(self, prediction):
        if not prediction.evidence:
            return {}
        try:
            return json.loads(prediction.evidence)
        except (TypeError, ValueError):
            return {}

    def _parse_iso_datetime(self, value):
        if not value:
            return None

        try:
            if isinstance(value, str) and value.endswith("Z"):
                value = value.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is not None:
                return parsed.replace(tzinfo=None)
            return parsed
        except (TypeError, ValueError):
            return None

    def _format_freshness(self, freshness_iso):
        freshness = self._parse_iso_datetime(freshness_iso)
        if not freshness:
            return "Unknown"

        age = datetime.utcnow() - freshness
        hours = int(age.total_seconds() // 3600)
        if hours < 1:
            age_display = "Updated <1 hour ago"
        elif hours < 24:
            age_display = f"Updated {hours} hours ago"
        else:
            age_display = f"Updated {hours // 24} days ago"

        return f"{age_display} ({freshness.isoformat()} UTC)"

    def _confidence_label_from_score(self, score):
        if score is None:
            return "Low"
        if score >= 0.75:
            return "High"
        if score >= 0.5:
            return "Medium"
        return "Low"

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
