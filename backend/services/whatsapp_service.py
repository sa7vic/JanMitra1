from twilio.rest import Client
from config import Config
from models.database import db, WhatsAppConversation, User
from services.ai_processor import AIProcessor
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        """
        Initialize Twilio WhatsApp service with credentials
        from environment.
        """
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.whatsapp_number = Config.TWILIO_WHATSAPP_NUMBER
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            logger.warning("⚠️ Twilio credentials not fully configured")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("✅ Twilio WhatsApp service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twilio client: {e}")
                self.client = None
        
        self.ai_processor = AIProcessor()
    
    def process_incoming_message(self, from_number, message_body, message_sid):
        """
        Process incoming WhatsApp message and generate AI response.
        
        Args:
            from_number: WhatsApp phone number of sender
                (e.g., "whatsapp:+919876543210")
            message_body: Text content of the message
            message_sid: Twilio message SID for tracking
            
        Returns:
            str: AI-generated response to send back
        """
        try:
            # Clean phone number (remove whatsapp: prefix if present)
            clean_phone = from_number.replace('whatsapp:', '').strip()
            
            # Log incoming message
            msg_preview = message_body[:50] + "..." if len(message_body) > 50 else message_body
            logger.info(f"📩 Incoming message from {clean_phone}: {msg_preview}")
            
            # Find or create user based on phone number
            user = User.query.filter_by(phone=clean_phone).first()
            user_id = user.id if user else None
            
            # Save incoming message to database
            conversation = WhatsAppConversation(
                phone_number=clean_phone,
                message=message_body,
                message_type='incoming',
                user_id=user_id,
                session_id=message_sid,
                status='processing'
            )
            db.session.add(conversation)
            db.session.commit()
            
            # Get conversation context for continuity
            context = self._get_conversation_context(clean_phone)
            
            # Process message with JanMitra AI
            ai_response = self._generate_ai_response(
                message_body, context, user
            )
            
            # Update conversation with response
            conversation.response = ai_response
            conversation.status = 'processed'
            db.session.commit()
            
            # Save outgoing message
            outgoing_conversation = WhatsAppConversation(
                phone_number=clean_phone,
                message=ai_response,
                response=message_body,
                message_type='outgoing',
                user_id=user_id,
                session_id=message_sid,
                status='sent'
            )
            db.session.add(outgoing_conversation)
            db.session.commit()
            
            logger.info(f"✅ Processed message for {clean_phone}")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            
            # Update conversation status
            if 'conversation' in locals():
                conversation.status = 'failed'
                conversation.error_message = str(e)
                db.session.commit()
            
            # Return fallback response
            return self._get_fallback_response()
    
    def _generate_ai_response(self, message, context, user=None):
        """
        Generate AI response using JanMitra AI processor.
        
        Args:
            message: User's message text
            context: Previous conversation context
            user: User object if available
            
        Returns:
            str: AI-generated response
        """
        try:
            # Handle common commands
            message_lower = message.lower().strip()
            
            if message_lower in ['hi', 'hello', 'hey', 'namaste', 'start']:
                return self._get_welcome_message(user)
            
            if message_lower in ['help', 'commands', 'menu']:
                return self._get_help_message()
            
            if message_lower in ['about', 'what is janmitra', 'who are you']:
                return self._get_about_message()
            
            # Build enhanced question with context
            enhanced_question = message
            if context:
                enhanced_question = f"Previous context: {context}\n\nCurrent question: {message}"
            
            # Use JanMitra AI processor to answer
            ai_response = self.ai_processor.answer_question(enhanced_question)
            
            # Add WhatsApp-friendly formatting
            formatted_response = self._format_for_whatsapp(ai_response)
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"❌ Error generating AI response: {e}")
            return self._get_fallback_response()
    
    def _get_conversation_context(self, phone_number, limit=3):
        """
        Retrieve recent conversation history for context.
        
        Args:
            phone_number: User's phone number
            limit: Number of recent messages to retrieve
            
        Returns:
            str: Formatted conversation context
        """
        try:
            # Get recent conversations from last 30 minutes
            time_threshold = datetime.utcnow() - timedelta(minutes=30)
            
            recent_conversations = WhatsAppConversation.query.filter(
                WhatsAppConversation.phone_number == phone_number,
                WhatsAppConversation.created_at >= time_threshold,
                WhatsAppConversation.status == 'processed'
            ).order_by(
                WhatsAppConversation.created_at.desc()
            ).limit(limit).all()
            
            if not recent_conversations:
                return ""
            
            # Format context
            context_parts = []
            for conv in reversed(recent_conversations):
                if conv.message_type == 'incoming':
                    context_parts.append(f"User: {conv.message}")
                    if conv.response:
                        context_parts.append(f"JanMitra: {conv.response}")
            
            return " | ".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation context: {e}")
            return ""
    
    def send_message(self, to_number, message):
        """
        Send WhatsApp message to a user.
        
        Args:
            to_number: Recipient phone number (with or without whatsapp: prefix)
            message: Message text to send
            
        Returns:
            dict: Result with status and message_sid or error
        """
        if not self.client:
            logger.error("❌ Twilio client not initialized")
            return {'status': 'error', 'error': 'Twilio client not configured'}
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            # Send message via Twilio
            message_obj = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            
            logger.info(f"✅ Message sent to {to_number}: {message_obj.sid}")
            
            return {
                'status': 'sent',
                'message_sid': message_obj.sid,
                'to': to_number
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending message to {to_number}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _format_for_whatsapp(self, text):
        """
        Format text for better WhatsApp display.
        
        Args:
            text: Text to format
            
        Returns:
            str: WhatsApp-formatted text
        """
        # Limit length for WhatsApp (max 1600 chars)
        if len(text) > 1500:
            text = text[:1500] + "...\n\n_Message truncated. Ask for more details if needed._"
        
        # Add JanMitra signature
        if not text.endswith("- JanMitra"):
            text += "\n\n_- JanMitra AI_"
        
        return text
    
    def _get_welcome_message(self, user=None):
        """Generate welcome message."""
        name = user.name if user and user.name else "there"
        
        return f"""🙏 *Namaste {name}!*

Welcome to *JanMitra AI* 🇮🇳

I'm your intelligent assistant for:
✅ Government schemes & eligibility
✅ Latest news & policies
✅ Grievance reporting
✅ Fact checking
✅ Price information
✅ Crisis predictions

Just send me your question! Examples:
"What schemes am I eligible for?"
"Latest news on agriculture"
"Petrol prices in Delhi"

Type *help* for more options.

_- JanMitra AI_"""
    
    def _get_help_message(self):
        """Generate help message."""
        return """📖 *JanMitra AI - Help Menu*

*What I can help with:*

🔹 *Schemes* - Ask about government schemes
🔹 *News* - Get latest updates on any topic
🔹 *Prices* - Check commodity prices
🔹 *Reports* - Report civic issues
🔹 *Fact Check* - Verify claims
🔹 *Predictions* - Crisis forecasts

*Example Questions:*
• "What schemes are available for farmers?"
• "Latest news on education policy"
• "Is petrol price increasing?"
• "Verify: PM announced new scheme"

Just type your question naturally!

_- JanMitra AI_"""
    
    def _get_about_message(self):
        """Generate about message."""
        return """🇮🇳 *About JanMitra AI*

JanMitra is India's intelligent governance assistant, powered by advanced AI.

*Key Features:*
✅ Real-time news analysis
✅ Government scheme matching
✅ Crisis prediction
✅ Fact verification
✅ Citizen reporting
✅ Knowledge graph

Built to empower every Indian with information and insights for better decision-making.

Ask me anything about India! 🚀

_- JanMitra AI_"""
    
    def _get_fallback_response(self):
        """Generate fallback response when AI fails."""
        return """⚠️ *Sorry, I encountered an issue processing your message.*

Please try:
• Rephrasing your question
• Asking something more specific
• Typing *help* for guidance

Our team has been notified.

_- JanMitra AI_"""
    
    def get_conversation_history(self, phone_number, limit=20):
        """
        Get conversation history for a phone number.
        
        Args:
            phone_number: User's phone number
            limit: Number of conversations to retrieve
            
        Returns:
            list: List of conversation dictionaries
        """
        try:
            clean_phone = phone_number.replace('whatsapp:', '').strip()
            
            conversations = WhatsAppConversation.query.filter_by(
                phone_number=clean_phone
            ).order_by(
                WhatsAppConversation.created_at.desc()
            ).limit(limit).all()
            
            return [conv.to_dict() for conv in conversations]
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return []
    
    def get_stats(self):
        """Get WhatsApp service statistics."""
        try:
            total_conversations = WhatsAppConversation.query.count()
            total_users = db.session.query(
                WhatsAppConversation.phone_number
            ).distinct().count()
            
            processed = WhatsAppConversation.query.filter_by(
                status='processed'
            ).count()
            
            failed = WhatsAppConversation.query.filter_by(
                status='failed'
            ).count()
            
            # Get conversations from last 24 hours
            time_threshold = datetime.utcnow() - timedelta(hours=24)
            recent_conversations = WhatsAppConversation.query.filter(
                WhatsAppConversation.created_at >= time_threshold
            ).count()
            
            return {
                'total_conversations': total_conversations,
                'unique_users': total_users,
                'processed': processed,
                'failed': failed,
                'last_24h': recent_conversations
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}
