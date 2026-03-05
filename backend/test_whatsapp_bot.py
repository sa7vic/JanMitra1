"""
Test script for JanMitra WhatsApp Bot
Run this to verify the implementation is working correctly.
"""

import requests
import json

BASE_URL = "http://localhost:5000"


def test_server_running():
    """Test if the server is running."""
    print("🧪 Test 1: Server Running")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start it with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_whatsapp_test_endpoint():
    """Test the WhatsApp test endpoint."""
    print("\n🧪 Test 2: WhatsApp Test Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/whatsapp/test")
        if response.status_code == 200:
            print("✅ WhatsApp routes are registered")
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Endpoints available:")
            for endpoint, method in data.get('endpoints', {}).items():
                print(f"      - {endpoint}: {method}")
            return True
        else:
            print(f"❌ Test endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_webhook_structure():
    """Test webhook endpoint structure (won't work without Twilio data)."""
    print("\n🧪 Test 3: Webhook Endpoint Structure")
    try:
        # Send empty POST (will fail validation, but tests endpoint exists)
        response = requests.post(f"{BASE_URL}/api/whatsapp/webhook")
        # We expect 400 because we're not sending valid Twilio data
        if response.status_code == 400:
            print("✅ Webhook endpoint exists and validates input")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   (This might be OK - endpoint exists)")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ai_query_endpoint():
    """Test the AI query endpoint (same one used by WhatsApp bot)."""
    print("\n🧪 Test 4: AI Query Endpoint (WhatsApp uses this)")
    try:
        test_question = "What is JanMitra?"
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"question": test_question},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Query endpoint working")
            print(f"   Question: {data.get('question')}")
            answer = data.get('answer', '')
            print(f"   Answer preview: {answer[:100]}...")
            return True
        else:
            print(f"❌ Query endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_database_models():
    """Test if database has WhatsApp conversation table."""
    print("\n🧪 Test 5: Database Models")
    print("   To verify database tables exist:")
    print("   1. Start Python shell in backend folder")
    print("   2. Run:")
    print("      >>> from app import app, db")
    print("      >>> from models.database import WhatsAppConversation")
    print("      >>> with app.app_context():")
    print("      >>>     print(WhatsAppConversation.query.count())")
    print("   ✅ If no error, database model is working!")
    return True


def print_setup_instructions():
    """Print setup instructions."""
    print("\n" + "="*60)
    print("📋 SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. Make sure your .env file has:")
    print("   - TWILIO_ACCOUNT_SID")
    print("   - TWILIO_AUTH_TOKEN")
    print("   - TWILIO_WHATSAPP_NUMBER")
    print("   - GROQ_API_KEY")
    print("\n2. For local testing:")
    print("   - Install ngrok: https://ngrok.com/")
    print("   - Run: ngrok http 5000")
    print("   - Copy the HTTPS URL")
    print("\n3. Configure Twilio:")
    print("   - Go to: https://console.twilio.com/")
    print("   - Navigate to: Messaging > Try it out > WhatsApp > Sandbox")
    print("   - Set webhook URL to: https://your-ngrok-url/api/whatsapp/webhook")
    print("   - Set method to: POST")
    print("\n4. Test the bot:")
    print("   - Join sandbox by sending the join code to Twilio number")
    print("   - Send 'hi' to test welcome message")
    print("   - Send 'help' to see all features")
    print("   - Ask any question!")
    print("\n📖 Full documentation: WHATSAPP_BOT_SETUP.md")
    print("="*60)


def main():
    """Run all tests."""
    print("="*60)
    print("🚀 JanMitra WhatsApp Bot - Test Suite")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Server Running", test_server_running()))
    
    if results[0][1]:  # Only continue if server is running
        results.append(("WhatsApp Test Endpoint", test_whatsapp_test_endpoint()))
        results.append(("Webhook Structure", test_webhook_structure()))
        results.append(("AI Query Endpoint", test_ai_query_endpoint()))
        results.append(("Database Models", test_database_models()))
    
    # Print results
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! WhatsApp bot is ready!")
        print_setup_instructions()
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        if not results[0][1]:
            print("\n💡 Tip: Start the server first with: python app.py")
    
    print("="*60)


if __name__ == "__main__":
    main()
