from models.database import db, Article, Entity, Prediction
from services.ai_processor import AIProcessor
from datetime import datetime, timedelta
import json
import re

class CrisisPredictor:
    def __init__(self):
        self.ai_processor = AIProcessor()
        
    def analyze_trends(self):
        """Analyze recent articles and generate real predictions using AI"""
        
        print("🔮 Starting AI-powered prediction analysis...")
        
        # Get recent articles (last 7 days)
        recent_articles = Article.query.order_by(Article.created_at.desc()).limit(100).all()
        
        if len(recent_articles) < 10:
            print("⚠️ Not enough articles for prediction. Need at least 10.")
            return []
        
        # Group articles by category
        categories = {}
        for article in recent_articles:
            cat = article.category or 'general'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        predictions = []
        
        # Analyze each category
        for category, articles in categories.items():
            if len(articles) < 3:
                continue
                
            print(f"📊 Analyzing {len(articles)} {category} articles...")
            
            # Build context from articles
            context = self._build_context(articles)
            
            # Ask AI to generate predictions
            prediction = self._ai_generate_prediction(category, context, articles)
            
            if prediction:
                predictions.append(prediction)
        
        # Save predictions to database
        for pred_data in predictions:
            # Check if similar prediction exists
            existing = Prediction.query.filter(
                Prediction.title.like(f"%{pred_data['title'][:30]}%"),
                Prediction.status == 'active'
            ).first()
            
            if not existing:
                prediction = Prediction(**pred_data)
                db.session.add(prediction)
                print(f"✅ Created: {pred_data['title']}")
        
        db.session.commit()
        return predictions
    
    def _build_context(self, articles):
        """Build summarized context from articles"""
        context = []
        for article in articles[:10]:  # Top 10 most recent
            context.append(f"• {article.title}\n  {article.content[:200]}...")
        return "\n\n".join(context)
    
    def _ai_generate_prediction(self, category, context, articles):
        """Use AI to generate real prediction from context"""
        
        if not self.ai_processor.client:
            print("⚠️ Groq not available, skipping AI prediction")
            return None
        
        prompt = f"""You are an expert crisis prediction system for India. Analyze these recent news articles and identify ONE specific, actionable crisis/trend that could develop.

CATEGORY: {category}

RECENT NEWS:
{context}

Generate a JSON prediction with:
{{
    "title": "Short, specific prediction title",
    "description": "Detailed 2-3 sentence explanation with numbers/facts",
    "severity": "high|medium|low",
    "confidence": 0.0-1.0 (be realistic, not overconfident),
    "days_ahead": 3-30 (when will this happen),
    "location": "Specific city/state or National",
    "evidence": {{
        "key_indicator_1": "value",
        "key_indicator_2": "value",
        "trend": "increasing|stable|decreasing"
    }}
}}

Rules:
- Be SPECIFIC (not vague like "economic concerns")
- Use NUMBERS from the articles
- Only predict if you see a real trend (confidence >0.65)
- Return "null" if no clear prediction possible

Return ONLY valid JSON or null:"""

        try:
            response = self.ai_processor.client.chat.completions.create(
                model=self.ai_processor.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=512,
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.lower() == 'null' or 'no clear prediction' in result_text.lower():
                print(f"  → No prediction for {category}")
                return None
            
            # Clean JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            # Validate
            if result.get('confidence', 0) < 0.65:
                print(f"  → Confidence too low: {result.get('confidence')}")
                return None
            
            # Build prediction data
            prediction_data = {
                'title': result['title'],
                'description': result['description'],
                'category': category,
                'severity': result.get('severity', 'medium'),
                'confidence': result['confidence'],
                'predicted_date': datetime.utcnow() + timedelta(days=result.get('days_ahead', 7)),
                'location': result.get('location', 'National'),
                'evidence': json.dumps(result.get('evidence', {})),
                'status': 'active'
            }
            
            return prediction_data
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse error: {e}")
            print(f"  Response was: {result_text[:200]}")
            return None
        except Exception as e:
            print(f"  ❌ AI prediction error: {e}")
            return None
    
    def _extract_location(self, text):
        """Extract Indian location from text"""
        locations = [
            'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad',
            'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Punjab', 'Maharashtra',
            'Karnataka', 'Tamil Nadu', 'West Bengal', 'Gujarat', 'Rajasthan',
            'Uttar Pradesh', 'Kerala', 'Madhya Pradesh', 'Andhra Pradesh',
            'Telangana', 'Bihar', 'Odisha', 'Haryana'
        ]
        
        text_lower = text.lower()
        for location in locations:
            if location.lower() in text_lower:
                return location
        
        return 'National'