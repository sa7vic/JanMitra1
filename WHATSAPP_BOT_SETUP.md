# JanMitra WhatsApp Bot - Setup Guide

## Overview
A complete WhatsApp bot integration that works exactly like the JanMitra AI system. Users can ask questions, get government scheme information, check news, report issues, and more - all through WhatsApp.

## Features Implemented

### 1. **Core Functionality**
- ✅ Receive incoming WhatsApp messages via Twilio webhook
- ✅ Process messages using JanMitra AI processor
- ✅ Send AI-generated responses back to users
- ✅ Conversation history tracking with context awareness
- ✅ Complete error handling and logging

### 2. **Database Schema**
- ✅ `WhatsAppConversation` model for storing all message history
- ✅ Links to User accounts when phone number is registered
- ✅ Session tracking for conversation continuity
- ✅ Status tracking (pending, processed, failed)

### 3. **WhatsApp Service** (`services/whatsapp_service.py`)
- AI-powered message processing using existing JanMitra AI
- Conversation context management (30-minute window)
- Built-in commands: hello, help, about
- WhatsApp-friendly message formatting
- Twilio integration for sending/receiving messages
- Statistics and analytics

### 4. **API Endpoints** (`routes/whatsapp.py`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/whatsapp/webhook` | POST | No | Twilio webhook for incoming messages |
| `/api/whatsapp/status` | POST | No | Twilio status callback |
| `/api/whatsapp/send` | POST | JWT | Send message to user (gov/admin only) |
| `/api/whatsapp/history/<phone>` | GET | JWT | Get conversation history |
| `/api/whatsapp/stats` | GET | JWT | Get service statistics (gov/admin only) |
| `/api/whatsapp/test` | GET | No | Test endpoint to verify setup |

## Setup Instructions

### Step 1: Verify Environment Variables
Make sure your `.env` file contains:
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
GROQ_API_KEY=your_groq_api_key
```

### Step 2: Install/Verify Dependencies
The required package `twilio==8.10.0` is already in `requirements.txt`. No additional installation needed.

### Step 3: Start the Backend Server
```bash
cd backend
python app.py
```

The server should start on `http://localhost:5000`.

### Step 4: Configure Twilio Webhook

#### For Testing (Local Development):
1. Install ngrok: https://ngrok.com/
2. Run ngrok:
   ```bash
   ngrok http 5000
   ```
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

#### In Twilio Console:
1. Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Under "Sandbox Configuration":
   - **WHEN A MESSAGE COMES IN**: `https://your-ngrok-url.ngrok.io/api/whatsapp/webhook`
   - **METHOD**: `HTTP POST`
3. Save configuration

### Step 5: Test the Bot

#### 5.1 Join Twilio WhatsApp Sandbox
1. In Twilio console WhatsApp sandbox page, you'll see a join code
2. Send that code to the Twilio WhatsApp number shown (usually `+1 415 523 8886`)
3. Example: `join happy-elephant` (your code will be different)

#### 5.2 Send Test Messages
Once joined, send these messages to test:

**Test 1: Welcome Message**
```
Hi
```
Expected: Welcome message with feature overview

**Test 2: Help Command**
```
help
```
Expected: List of capabilities and example questions

**Test 3: AI Query**
```
What government schemes are available for farmers?
```
Expected: AI-generated answer based on JanMitra knowledge base

**Test 4: News Query**
```
Latest news on education policy
```
Expected: News summary from JanMitra AI

**Test 5: General Question**
```
What is the current petrol price?
```
Expected: AI response with relevant information

## Architecture

### Message Flow
```
User WhatsApp Message
    ↓
Twilio Webhook
    ↓
/api/whatsapp/webhook
    ↓
WhatsAppService.process_incoming_message()
    ↓
Save to Database (WhatsAppConversation)
    ↓
Get Conversation Context (last 30 mins)
    ↓
AIProcessor.answer_question()
    ↓
Format Response for WhatsApp
    ↓
Save Response to Database
    ↓
Return TwiML Response
    ↓
Twilio sends to User
```

### Built-in Commands
- `hi`, `hello`, `hey`, `namaste`, `start` → Welcome message
- `help`, `commands`, `menu` → Help menu
- `about`, `what is janmitra`, `who are you` → About JanMitra
- Any other text → Processed by JanMitra AI

### Context Management
- Stores last 3 conversations in 30-minute window
- Provides context to AI for better responses
- Tracks conversation sessions by message SID

## API Usage Examples

### Send Message (Government/Admin)
```bash
curl -X POST http://localhost:5000/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "phone": "+919876543210",
    "message": "Important update from JanMitra: New scheme launched!"
  }'
```

### Get Conversation History
```bash
curl http://localhost:5000/api/whatsapp/history/+919876543210?limit=10 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Statistics
```bash
curl http://localhost:5000/api/whatsapp/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Schema

### WhatsAppConversation Table
```python
{
    'id': Integer,
    'phone_number': String(20),        # User's phone number
    'message': Text,                   # User's message or bot's message
    'response': Text,                  # Response sent (for incoming) or received (for outgoing)
    'message_type': String(20),        # 'incoming' or 'outgoing'
    'user_id': Integer,                # FK to User (if registered)
    'session_id': String(100),         # Twilio message SID
    'status': String(20),              # 'pending', 'processed', 'failed', 'sent'
    'error_message': Text,             # Error details if failed
    'created_at': DateTime
}
```

## Error Handling

### The system handles:
1. **Missing credentials** → Warning logged, service continues in fallback mode
2. **Twilio API errors** → Logged, fallback response sent to user
3. **AI processing errors** → Logged, friendly error message sent to user
4. **Database errors** → Logged, conversation continues but may not be saved
5. **Invalid webhook data** → Returns 400 Bad Request

### Logging
All operations are logged with emojis for easy monitoring:
- 📩 Incoming message
- ✅ Success
- ❌ Error
- ⚠️ Warning
- 📊 Status update

## Testing Checklist

- [ ] Server starts without errors
- [ ] `/api/whatsapp/test` endpoint returns 200 OK
- [ ] WhatsApp message sent to bot triggers webhook
- [ ] Bot responds with welcome message to "hi"
- [ ] Bot responds to help command
- [ ] Bot answers general questions using AI
- [ ] Conversation history is saved in database
- [ ] Context is maintained across messages (within 30 mins)
- [ ] Error messages work when AI fails
- [ ] Gov/admin can send messages via API
- [ ] Statistics endpoint works for gov/admin

## Troubleshooting

### Bot doesn't respond
1. Check server logs for errors
2. Verify ngrok is running and URL is correct in Twilio
3. Check `.env` file has correct Twilio credentials
4. Verify you've joined the Twilio sandbox

### AI responses are generic
1. Check `GROQ_API_KEY` is set in `.env`
2. Verify AIProcessor initialized successfully (check startup logs)
3. Ensure database has articles/entities (run `generate_sample_data.py`)

### Webhook returns 400
1. Check Twilio webhook configuration
2. Verify POST method is selected
3. Check server logs for validation errors

### Context not working
1. Check database has WhatsAppConversation table
2. Verify conversations are being saved
3. Check system time is correct (uses 30-minute window)

## Production Deployment

### For production:
1. Deploy backend to a server with HTTPS
2. Update Twilio webhook URL to production URL
3. Set strong `SECRET_KEY` in environment
4. Enable proper logging and monitoring
5. Consider rate limiting for webhook endpoint
6. Set up Twilio phone number (not sandbox) for production use
7. Implement phone number verification for sensitive operations

## Security Features

1. **JWT Authentication**: Required for send, history, and stats endpoints
2. **Role-based Access**: Gov/admin roles for privileged operations
3. **User Isolation**: Users can only see their own conversation history
4. **Input Validation**: All inputs validated before processing
5. **Error Masking**: Sensitive errors not exposed to end users

## Monitoring

### Key Metrics (via `/api/whatsapp/stats`):
- Total conversations
- Unique users
- Processed messages
- Failed messages
- Last 24h activity

### Recommended Monitoring:
- Response time of webhook endpoint
- AI processing time
- Failed message rate
- Active users count
- Database size

## Extending the Bot

### Add Custom Commands
Edit `WhatsAppService._generate_ai_response()`:
```python
if message_lower == 'your_command':
    return "Your custom response"
```

### Add Rich Media
Twilio supports:
- Images
- Documents
- Location
- Contact cards

Update webhook handler to process `MediaUrl` parameter.

### Add Interactive Buttons
Use Twilio's Content API to send interactive messages with buttons.

## Support

For issues:
1. Check logs in terminal
2. Test endpoint at `/api/whatsapp/test`
3. Verify all environment variables are set
4. Check Twilio console for webhook errors

---

**Status**: ✅ **FULLY IMPLEMENTED AND READY TO USE**

The WhatsApp bot is now integrated with JanMitra AI and ready for testing!
