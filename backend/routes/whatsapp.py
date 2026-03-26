from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.whatsapp_service import WhatsAppService
from models.database import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__)
whatsapp_service = WhatsAppService()


@whatsapp_bp.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Twilio WhatsApp webhook endpoint.
    Receives incoming messages and sends AI-generated responses.
    
    This endpoint is called by Twilio when a message is received.
    Configure this in your Twilio console:
    https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
    
    Webhook URL format: https://your-domain.com/api/whatsapp/webhook
    """
    try:
        # Get message details from Twilio request
        from_number = request.values.get('From', '')
        message_body = request.values.get('Body', '')
        message_sid = request.values.get('MessageSid', '')
        
        logger.info(f"📩 Webhook received from {from_number}")
        
        # Validate required fields
        if not from_number or not message_body:
            logger.error("❌ Missing required fields in webhook request")
            return '', 400
        
        # Process message and get AI response
        ai_response = whatsapp_service.process_incoming_message(
            from_number=from_number,
            message_body=message_body,
            message_sid=message_sid
        )
        
        # Create Twilio response
        twiml_response = MessagingResponse()
        twiml_response.message(ai_response)
        
        logger.info(f"✅ Response sent to {from_number}")
        
        return str(twiml_response), 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        
        # Send error message to user
        twiml_response = MessagingResponse()
        error_msg = (
            "⚠️ Sorry, something went wrong. "
            "Please try again later.\n\n_- JanMitra AI_"
        )
        twiml_response.message(error_msg)
        
        return str(twiml_response), 200, {'Content-Type': 'application/xml'}


@whatsapp_bp.route('/status', methods=['POST'])
def whatsapp_status():
    """
    Twilio status callback endpoint.
    Receives delivery status updates for sent messages.
    
    Configure this as the status callback URL in Twilio console.
    """
    try:
        message_sid = request.values.get('MessageSid', '')
        message_status = request.values.get('MessageStatus', '')
        
        logger.info(f"📊 Message {message_sid} status: {message_status}")
        
        # You can update conversation status here if needed
        # For now, just log it
        
        return '', 200
        
    except Exception as e:
        logger.error(f"❌ Status callback error: {e}")
        return '', 200


@whatsapp_bp.route('/send', methods=['POST'])
@jwt_required()
def send_whatsapp_message():
    """
    API endpoint to send WhatsApp message to a user.
    Requires JWT authentication (for government/admin users).
    
    Request body:
    {
        "phone": "+919876543210",
        "message": "Your message text"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        # Check if user has permission (government or admin role)
        if not user or user.role not in ['gov', 'government', 'admin']:
            return jsonify({
                'error': (
                    'Unauthorized. Only government/admin users '
                    'can send messages.'
                )
            }), 403
        
        data = request.get_json()
        phone = data.get('phone', '')
        message = data.get('message', '')
        
        if not phone or not message:
            return jsonify({
                'error': 'Phone number and message are required'
            }), 400
        
        # Send message
        result = whatsapp_service.send_message(phone, message)
        
        if result.get('status') == 'sent':
            return jsonify({
                'success': True,
                'message': 'Message sent successfully',
                'message_sid': result.get('message_sid')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to send message')
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Send message error: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@whatsapp_bp.route('/history/<phone>', methods=['GET'])
@jwt_required()
def get_conversation_history(phone):
    """
    Get WhatsApp conversation history for a phone number.
    Requires JWT authentication.
    
    Query parameters:
    - limit: Number of conversations to retrieve (default: 20)
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check permission: user can only see their own history,
        # or government/admin can see anyone's
        clean_phone = phone.replace('whatsapp:', '').replace('+', '').strip()
        user_phone = user.phone.replace('+', '').strip() if user.phone else ''
        
        if user.role not in ['gov', 'government', 'admin'] and clean_phone != user_phone:
            return jsonify({
                'error': (
                    'Unauthorized. You can only view your own '
                    'conversation history.'
                )
            }), 403
        
        limit = request.args.get('limit', 20, type=int)
        
        # Get conversation history
        history = whatsapp_service.get_conversation_history(phone, limit=limit)
        
        return jsonify({
            'phone': phone,
            'conversations': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Get history error: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@whatsapp_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_whatsapp_stats():
    """
    Get WhatsApp service statistics.
    Requires JWT authentication (government/admin only).
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        # Check if user has permission
        if not user or user.role not in ['gov', 'government', 'admin']:
            return jsonify({
                'error': (
                    'Unauthorized. Only government/admin users '
                    'can view statistics.'
                )
            }), 403
        
        stats = whatsapp_service.get_stats()
        
        return jsonify({
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Get stats error: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@whatsapp_bp.route('/test', methods=['GET'])
def test_whatsapp():
    """
    Test endpoint to verify WhatsApp routes are registered.
    """
    return jsonify({
        'status': 'online',
        'service': 'JanMitra WhatsApp Bot',
        'version': '1.0.0',
        'endpoints': {
            'webhook': '/api/whatsapp/webhook (POST)',
            'status': '/api/whatsapp/status (POST)',
            'send': '/api/whatsapp/send (POST, auth required)',
            'history': '/api/whatsapp/history/<phone> (GET, auth required)',
            'stats': '/api/whatsapp/stats (GET, auth required)'
        },
        'setup_instructions': {
            '1': 'Configure webhook URL in Twilio console',
            '2': (
                'Set environment variables: TWILIO_ACCOUNT_SID, '
                'TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER'
            ),
            '3': 'Send a WhatsApp message to your Twilio number to test'
        }
    }), 200
