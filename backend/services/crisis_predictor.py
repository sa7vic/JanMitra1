from datetime import datetime, timedelta
import json
import re
import statistics

from models.database import Article, Prediction, db


class CrisisPredictor:
    def __init__(self):
        self.indicator_specs = {
            "commodity_food": {
                "label": "Food commodities",
                "signal_type": "Leading",
                "keywords": [
                    "wheat",
                    "rice",
                    "onion",
                    "tomato",
                    "pulses",
                    "food prices",
                    "mandi",
                ],
                "freshness_hours": 48,
                "min_samples": 2,
                "delta_threshold": 4.0,
                "z_threshold": 1.5,
            },
            "commodity_energy": {
                "label": "Energy commodities",
                "signal_type": "Leading",
                "keywords": [
                    "crude",
                    "brent",
                    "oil",
                    "petrol",
                    "diesel",
                    "fuel prices",
                ],
                "freshness_hours": 24,
                "min_samples": 2,
                "delta_threshold": 3.0,
                "z_threshold": 1.5,
            },
            "commodity_metals": {
                "label": "Industrial metals",
                "signal_type": "Leading",
                "keywords": [
                    "copper",
                    "aluminium",
                    "steel",
                    "metal prices",
                ],
                "freshness_hours": 24,
                "min_samples": 2,
                "delta_threshold": 3.0,
                "z_threshold": 1.5,
            },
            "bond_yield_10y": {
                "label": "10Y G-sec yields",
                "signal_type": "Leading",
                "keywords": [
                    "10-year yield",
                    "10y g-sec",
                    "g-sec yield",
                    "bond yield",
                    "gsec",
                ],
                "freshness_hours": 24,
                "min_samples": 2,
                "delta_threshold": 0.15,
                "z_threshold": 1.4,
            },
            "currency_inr_usd": {
                "label": "INR/USD",
                "signal_type": "Leading",
                "keywords": [
                    "inr",
                    "rupee",
                    "usd",
                    "dollar",
                    "inr/usd",
                    "rupee weakens",
                ],
                "freshness_hours": 24,
                "min_samples": 2,
                "delta_threshold": 0.6,
                "z_threshold": 1.4,
            },
            "wpi": {
                "label": "WPI",
                "signal_type": "Leading",
                "keywords": [
                    "wpi",
                    "wholesale price index",
                    "wholesale inflation",
                ],
                "freshness_hours": 24 * 45,
                "min_samples": 2,
                "delta_threshold": 0.5,
                "z_threshold": 1.2,
            },
            "cpi": {
                "label": "CPI",
                "signal_type": "Lagging",
                "keywords": [
                    "cpi",
                    "consumer price index",
                    "retail inflation",
                ],
                "freshness_hours": 24 * 45,
                "min_samples": 2,
                "delta_threshold": 0.5,
                "z_threshold": 1.2,
            },
            "supply_chain": {
                "label": "Supply chain disruptions",
                "signal_type": "Leading",
                "keywords": [
                    "supply chain",
                    "shipment",
                    "logistics",
                    "port congestion",
                    "freight",
                ],
                "freshness_hours": 72,
                "min_samples": 2,
                "delta_threshold": 1.0,
                "z_threshold": 1.3,
            },
            "weather_food": {
                "label": "Weather impact on food",
                "signal_type": "Leading",
                "keywords": [
                    "rainfall deficit",
                    "heatwave",
                    "monsoon",
                    "crop damage",
                    "imd",
                    "drought",
                ],
                "freshness_hours": 72,
                "min_samples": 2,
                "delta_threshold": 1.0,
                "z_threshold": 1.3,
            },
        }

    def analyze_trends(self):
        """Generate near-real-time macro alerts from fresh signals."""
        now = datetime.utcnow()
        cutoff = now - timedelta(days=10)

        recent_articles = (
            Article.query.order_by(Article.created_at.desc()).limit(400).all()
        )
        recent_articles = [
            article
            for article in recent_articles
            if self._article_timestamp(article) >= cutoff
        ]

        if len(recent_articles) < 8:
            return []

        observations = self._extract_observations(recent_articles)
        events = self._detect_indicator_events(observations, now)
        events.extend(self._build_correlated_macro_events(events, now))

        predictions = [
            self._event_to_prediction(event)
            for event in events
        ]
        predictions = [prediction for prediction in predictions if prediction]

        created_predictions = []
        for pred_data in predictions:
            existing = Prediction.query.filter(
                Prediction.title == pred_data["title"],
                Prediction.status == "active",
                Prediction.created_at >= now - timedelta(hours=12),
            ).first()

            if existing:
                continue

            prediction = Prediction(**pred_data)
            db.session.add(prediction)
            created_predictions.append(pred_data)

        if created_predictions:
            db.session.commit()

        return created_predictions

    def _extract_observations(self, articles):
        observations = {
            indicator: []
            for indicator in self.indicator_specs
        }

        for article in articles:
            text = f"{article.title or ''} {article.content or ''}".lower()
            timestamp = self._article_timestamp(article)

            for indicator, spec in self.indicator_specs.items():
                if not any(word in text for word in spec["keywords"]):
                    continue

                value = self._extract_signal_value(text)
                if value is None:
                    value = self._heuristic_signal_value(text)

                observations[indicator].append(
                    {
                        "value": value,
                        "timestamp": timestamp,
                        "title": article.title,
                        "url": article.url,
                        "source": article.source,
                    }
                )

        return observations

    def _detect_indicator_events(self, observations, now):
        events = []

        for indicator, samples in observations.items():
            spec = self.indicator_specs[indicator]
            cutoff = now - timedelta(hours=spec["freshness_hours"])
            fresh_samples = [
                sample
                for sample in samples
                if sample["timestamp"] >= cutoff
            ]

            if len(fresh_samples) < spec["min_samples"]:
                continue

            ordered = sorted(
                fresh_samples,
                key=lambda item: item["timestamp"],
            )
            latest = ordered[-1]
            previous_values = [item["value"] for item in ordered[:-1]]

            if not previous_values:
                continue

            baseline = statistics.mean(previous_values)
            delta = latest["value"] - baseline
            if len(previous_values) > 1:
                std_dev = statistics.pstdev(previous_values)
            else:
                std_dev = 0.0

            z_score = delta / std_dev if std_dev > 0 else delta

            below_delta = abs(delta) < spec["delta_threshold"]
            below_z = abs(z_score) < spec["z_threshold"]
            if below_delta and below_z:
                continue

            direction = "up" if delta > 0 else "down"
            events.append(
                {
                    "indicator": indicator,
                    "indicator_label": spec["label"],
                    "signal_type": spec["signal_type"],
                    "direction": direction,
                    "delta": delta,
                    "z_score": z_score,
                    "latest_timestamp": latest["timestamp"],
                    "latest_title": latest["title"],
                    "latest_url": latest["url"],
                    "source": latest["source"],
                    "sample_count": len(ordered),
                    "freshness_hours": spec["freshness_hours"],
                }
            )

        return events

    def _build_correlated_macro_events(self, indicator_events, now):
        if not indicator_events:
            return []

        fresh_leading = [
            event
            for event in indicator_events
            if event["signal_type"] == "Leading"
            and event["latest_timestamp"] >= now - timedelta(hours=72)
        ]

        up_events = [
            event
            for event in fresh_leading
            if event["direction"] == "up"
        ]
        down_events = [
            event
            for event in fresh_leading
            if event["direction"] == "down"
        ]

        macro_events = []

        if len(up_events) >= 2:
            macro_events.append(
                self._build_macro_event_payload(
                    title="Inflation Pressure Building",
                    direction="up",
                    indicators=up_events,
                )
            )

        if len(down_events) >= 2:
            macro_events.append(
                self._build_macro_event_payload(
                    title="Inflation Pressure Easing",
                    direction="down",
                    indicators=down_events,
                )
            )

        return macro_events

    def _build_macro_event_payload(self, title, direction, indicators):
        most_recent = max(
            indicators,
            key=lambda item: item["latest_timestamp"],
        )
        confidence, confidence_label = self._confidence_from_quality(
            indicators
        )

        trigger_parts = []
        for event in indicators[:4]:
            sign = "+" if event["delta"] > 0 else ""
            trigger_parts.append(
                (
                    f"{event['indicator_label']} {sign}{event['delta']:.2f} "
                    f"(z={event['z_score']:.2f})"
                )
            )

        total_samples = sum(event["sample_count"] for event in indicators)
        uncertainty = (
            f"Direction={direction}; confidence={confidence_label}; "
            f"sample_size={total_samples}"
        )

        evidence = {
            "signal_type": "Leading",
            "data_freshness": most_recent["latest_timestamp"].isoformat(),
            "trigger_reason": "; ".join(trigger_parts),
            "supporting_indicators": [
                event["indicator_label"]
                for event in indicators
            ],
            "confidence_label": confidence_label,
            "confidence_basis": (
                "Data quality score from freshness, sample count, "
                "and indicator corroboration."
            ),
            "model": {
                "type": (
                    "Rule-based event detector "
                    "(z-score + short-term delta)"
                ),
                "assumptions": [
                    "Freshness windows are indicator-specific.",
                    "At least two leading indicators must align.",
                    "No timeline is emitted without a forecast model.",
                ],
                "uncertainty": uncertainty,
            },
            "sources": [
                {
                    "indicator": event["indicator_label"],
                    "source": event["source"],
                    "headline": event["latest_title"],
                    "url": event["latest_url"],
                    "timestamp": event["latest_timestamp"].isoformat(),
                }
                for event in indicators[:6]
            ],
        }

        return {
            "title": f"⚡ ALERT: {title}",
            "description": (
                "Multiple fresh leading indicators moved together. "
                "This is a near-real-time signal, not a "
                "historical-average summary."
            ),
            "category": "economy",
            "severity": "high" if len(indicators) >= 4 else "medium",
            "confidence": confidence,
            "predicted_date": None,
            "location": "National",
            "status": "active",
            "evidence": json.dumps(evidence),
        }

    def _event_to_prediction(self, event):
        if event.get("category") == "economy":
            return event

        confidence, confidence_label = self._confidence_from_quality([event])

        direction = "rose" if event["direction"] == "up" else "fell"
        trigger_reason = (
            f"{event['indicator_label']} {direction} by "
            f"{event['delta']:.2f} vs baseline "
            f"(z={event['z_score']:.2f})"
        )

        evidence = {
            "signal_type": event["signal_type"],
            "data_freshness": event["latest_timestamp"].isoformat(),
            "trigger_reason": trigger_reason,
            "supporting_indicators": [event["indicator_label"]],
            "confidence_label": confidence_label,
            "confidence_basis": (
                "Confidence reflects freshness and sample sufficiency, "
                "not arbitrary percentages."
            ),
            "model": {
                "type": (
                    "Rule-based event detector "
                    "(z-score + short-term delta)"
                ),
                "assumptions": [
                    "Minimum fresh samples required.",
                    "Threshold breach required for alerting.",
                ],
                "uncertainty": (
                    "single_indicator_signal=true; "
                    f"samples={event['sample_count']}"
                ),
            },
            "sources": [
                {
                    "indicator": event["indicator_label"],
                    "source": event["source"],
                    "headline": event["latest_title"],
                    "url": event["latest_url"],
                    "timestamp": event["latest_timestamp"].isoformat(),
                }
            ],
        }

        suffix = "Pressure" if event["direction"] == "up" else "Cooling"

        return {
            "title": f"⚡ ALERT: {event['indicator_label']} {suffix}",
            "description": (
                f"{event['indicator_label']} triggered a short-term "
                "deviation event from fresh observations."
            ),
            "category": "economy",
            "severity": "medium",
            "confidence": confidence,
            "predicted_date": None,
            "location": "National",
            "status": "active",
            "evidence": json.dumps(evidence),
        }

    def _confidence_from_quality(self, events):
        fresh_scores = []
        sample_scores = []

        for event in events:
            age_seconds = (
                datetime.utcnow() - event["latest_timestamp"]
            ).total_seconds()
            hours_old = max(age_seconds / 3600.0, 0.0)
            max_window = max(event["freshness_hours"], 1)
            freshness_ratio = max(0.0, 1.0 - (hours_old / max_window))
            fresh_scores.append(freshness_ratio)
            sample_scores.append(min(event["sample_count"] / 4.0, 1.0))

        freshness_component = (
            statistics.mean(fresh_scores) if fresh_scores else 0.0
        )
        sample_component = (
            statistics.mean(sample_scores) if sample_scores else 0.0
        )
        corroboration_component = min(len(events) / 4.0, 1.0)

        confidence = (
            (0.45 * freshness_component)
            + (0.30 * sample_component)
            + (0.25 * corroboration_component)
        )
        confidence = max(0.0, min(confidence, 1.0))

        if confidence >= 0.75:
            label = "High"
        elif confidence >= 0.5:
            label = "Medium"
        else:
            label = "Low"

        return confidence, label

    def _article_timestamp(self, article):
        return article.published_at or article.created_at or datetime.utcnow()

    def _extract_signal_value(self, text):
        percent_pattern = r"([+-]?\\d+(?:\\.\\d+)?)\\s*%"
        bps_pattern = r"([+-]?\\d+(?:\\.\\d+)?)\\s*bps"

        percent_matches = [
            float(match)
            for match in re.findall(percent_pattern, text)
        ]
        bps_matches = [
            float(match) / 100.0
            for match in re.findall(bps_pattern, text)
        ]

        values = percent_matches + bps_matches
        if not values:
            return None

        value = values[0]
        if value >= 0 and self._has_negative_direction(text):
            value = -value
        elif value <= 0 and self._has_positive_direction(text):
            value = abs(value)

        return value

    def _heuristic_signal_value(self, text):
        if self._has_positive_direction(text):
            return 1.0
        if self._has_negative_direction(text):
            return -1.0
        return 0.0

    def _has_positive_direction(self, text):
        markers = [
            "rise",
            "rising",
            "surge",
            "spike",
            "jump",
            "higher",
            "up",
            "increase",
            "tightening",
        ]
        return any(marker in text for marker in markers)

    def _has_negative_direction(self, text):
        markers = [
            "fall",
            "decline",
            "cooling",
            "lower",
            "drop",
            "down",
            "easing",
        ]
        return any(marker in text for marker in markers)
