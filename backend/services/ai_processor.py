import os
import json
from models.database import db, Entity, Relationship, Article

class AIProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.client = None
        self.model = 'llama-3.3-70b-versatile'
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                print("✅ Groq AI initialized successfully")
            except Exception as e:
                print(f"⚠️ Groq initialization failed: {e}")
                print("⚠️ AI features will use fallback mode")
        else:
            print("⚠️ No GROQ_API_KEY found. Using fallback mode.")
    
    def extract_entities_and_relationships(self, article):
        if not self.client:
            return self._fallback_extraction(article)
        
        prompt = f"""
Analyze this Indian news article and extract:

1. ENTITIES (people, places, events, policies, commodities, indicators)
2. RELATIONSHIPS (how entities are connected)

Article Title: {article.title}
Article Content: {article.content[:2000]}

Return ONLY valid JSON in this exact format:
{{
    "entities": [
        {{"name": "Entity Name", "type": "person|place|event|policy|commodity|indicator", "description": "brief description"}}
    ],
    "relationships": [
        {{"source": "Entity1", "target": "Entity2", "type": "causes|affects|relates_to", "context": "explanation"}}
    ]
}}

Focus on important entities relevant to governance, economy, health, agriculture.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            self.save_entities_and_relationships(result)
            
            return result
            
        except Exception as e:
            print(f"❌ AI Processing error: {e}")
            return self._fallback_extraction(article)
    
    def _fallback_extraction(self, article):
        entities = []
        relationships = []
        
        places = ['India', 'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 
                  'Hyderabad', 'Pune', 'Punjab', 'Maharashtra', 'Karnataka', 'Tamil Nadu']
        
        commodities = ['petrol', 'diesel', 'rice', 'wheat', 'onion', 'tomato', 
                       'gold', 'silver', 'crude oil']
        
        indicators = ['GDP', 'inflation', 'price', 'rate', 'growth']
        
        text = (article.title + " " + article.content).lower()
        
        for place in places:
            if place.lower() in text:
                entities.append({
                    "name": place,
                    "type": "place",
                    "description": f"Mentioned in {article.source}"
                })
        
        for commodity in commodities:
            if commodity in text:
                entities.append({
                    "name": commodity.title(),
                    "type": "commodity",
                    "description": f"Mentioned in context of {article.category}"
                })
        
        for indicator in indicators:
            if indicator in text:
                entities.append({
                    "name": indicator.upper(),
                    "type": "indicator",
                    "description": f"Economic indicator from {article.source}"
                })
        
        result = {
            "entities": entities[:10],
            "relationships": relationships
        }
        
        if entities:
            self.save_entities_and_relationships(result)
        
        return result
    
    def save_entities_and_relationships(self, result):
        entity_map = {}
        
        for entity_data in result.get('entities', []):
            entity = Entity.query.filter_by(name=entity_data['name']).first()
            
            if not entity:
                entity = Entity(
                    name=entity_data['name'],
                    type=entity_data.get('type', 'unknown'),
                    description=entity_data.get('description', ''),
                    data=json.dumps({})
                )
                db.session.add(entity)
                db.session.flush()
            
            entity_map[entity_data['name']] = entity.id
        
        for rel_data in result.get('relationships', []):
            source_id = entity_map.get(rel_data['source'])
            target_id = entity_map.get(rel_data['target'])
            
            if source_id and target_id:
                existing = Relationship.query.filter_by(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=rel_data['type']
                ).first()
                
                if not existing:
                    relationship = Relationship(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type=rel_data['type'],
                        context=rel_data.get('context', ''),
                        strength=0.7
                    )
                    db.session.add(relationship)
        
        try:
            db.session.commit()
        except Exception as e:
            print(f"❌ Error saving entities: {e}")
            db.session.rollback()
    
    def answer_question(self, question, context_data=None):
        if not context_data:
            context_data = self.get_relevant_context(question)
        
        if not self.client:
            return self._fallback_answer(question, context_data)
        
        prompt = f"""
You are JanMitra, India's national intelligence system. Answer this question clearly and informatively.

Question: {question}

Context from recent Indian news:
{context_data}

Provide a comprehensive answer that:
- Directly answers the question
- Uses data from the context
- Explains causes and effects
- Is easy to understand
- Is factual and balanced

Keep response under 250 words.

Answer:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=512,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Question answering error: {e}")
            return self._fallback_answer(question, context_data)
    
    def _fallback_answer(self, question, context_data):
        if "No specific recent news found" in context_data:
            return f"I found limited information about '{question}'. The system is still collecting data. Please try again in a few minutes or ask about a different topic."
        
        return f"Based on recent news:\n\n{context_data[:500]}...\n\nNote: This is a basic response. For AI-powered analysis, please configure GROQ_API_KEY."
    
    def get_relevant_context(self, question, max_articles=5):
        keywords = question.lower().split()
        
        articles = Article.query.order_by(Article.created_at.desc()).limit(50).all()
        
        relevant_articles = []
        for article in articles:
            text = (article.title + " " + article.content).lower()
            if any(keyword in text for keyword in keywords if len(keyword) > 3):
                relevant_articles.append(article)
                if len(relevant_articles) >= max_articles:
                    break
        
        if not relevant_articles:
            return "No specific recent news found on this topic."
        
        context = "\n\n".join([
            f"Source: {a.source} | {a.title}\n{a.content[:300]}..."
            for a in relevant_articles
        ])
        
        return context