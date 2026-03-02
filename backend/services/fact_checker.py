from models.database import db, Article, Entity, FactCheck
from services.ai_processor import AIProcessor
import json

class FactChecker:
    def __init__(self):
        self.ai_processor = AIProcessor()
    
    def verify_claim(self, claim, user_id=None):
        context = self._get_relevant_context(claim)
        
        if not self.ai_processor.client:
            return self._fallback_check(claim, context)
        
        prompt = f"""
You are a fact-checking system for India. Verify this claim:

CLAIM: {claim}

CONTEXT (Recent verified news):
{context}

Analyze and respond in JSON format:
{{
    "verdict": "TRUE|FALSE|PARTIALLY_TRUE|UNVERIFIED",
    "confidence": 0.0-1.0,
    "explanation": "detailed explanation",
    "sources": ["source1", "source2"]
}}

Be strict and evidence-based. If no clear evidence, mark as UNVERIFIED.
"""
        
        try:
            response = self.ai_processor.client.chat.completions.create(
                model=self.ai_processor.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=512,
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            fact_check = FactCheck(
                claim=claim,
                verdict=result['verdict'],
                confidence=result['confidence'],
                explanation=result['explanation'],
                sources=json.dumps(result.get('sources', [])),
                user_id=user_id
            )
            db.session.add(fact_check)
            db.session.commit()
            
            return result
            
        except Exception as e:
            print(f"❌ Fact check error: {e}")
            return self._fallback_check(claim, context)
    
    def _get_relevant_context(self, claim):
        keywords = claim.lower().split()
        articles = Article.query.order_by(Article.created_at.desc()).limit(100).all()
        
        relevant = []
        for article in articles:
            text = (article.title + " " + article.content).lower()
            if any(kw in text for kw in keywords if len(kw) > 3):
                relevant.append(article)
                if len(relevant) >= 5:
                    break
        
        if not relevant:
            return "No recent news found related to this claim."
        
        context = "\n\n".join([
            f"Source: {a.source}\n{a.title}\n{a.content[:200]}..."
            for a in relevant
        ])
        
        return context
    
    def _fallback_check(self, claim, context):
        if "No recent news found" in context:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 0.3,
                'explanation': 'Insufficient data to verify this claim. No recent news found on this topic.',
                'sources': []
            }
        
        common_fake_patterns = [
            r'government.*giving.*money.*everyone',
            r'free.*₹\d+.*scheme',
            r'WhatsApp.*forward.*get',
            r'click.*link.*prize'
        ]
        
        import re
        for pattern in common_fake_patterns:
            if re.search(pattern, claim.lower()):
                return {
                    'verdict': 'FALSE',
                    'confidence': 0.75,
                    'explanation': 'This claim matches common misinformation patterns. No official sources confirm this.',
                    'sources': []
                }
        
        return {
            'verdict': 'UNVERIFIED',
            'confidence': 0.5,
            'explanation': f'Based on recent news:\n\n{context[:300]}...\n\nUnable to fully verify. Check official sources.',
            'sources': []
        }