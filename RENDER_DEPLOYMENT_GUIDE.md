# Deploying JanMitra Backend to Render 🚀

## Why No Ngrok is Needed

**Ngrok is only for local development!** When you deploy to Render:
- ✅ Render provides a permanent public URL (e.g., `https://janmitra-backend.onrender.com`)
- ✅ This URL is always accessible from the internet
- ✅ WhatsApp webhooks can directly call this URL
- ❌ No need for tunneling or temporary URLs

---

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your code to GitHub
3. **API Keys Ready**:
   - Groq API Key
   - News API Key  
   - Twilio Account SID & Auth Token
   - Cloudinary credentials (if using image uploads)

---

## Step 1: Update Requirements for Production

Add `gunicorn` to your requirements.txt (already done in the included file):

```bash
# In backend directory
echo "gunicorn==21.2.0" >> requirements.txt
```

---

## Step 2: Update Database Configuration (Recommended)

For production, **use PostgreSQL** instead of SQLite. Update `config.py`:

```python
# In config.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'janmitra-dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Use PostgreSQL in production, SQLite in development
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        # Render provides DATABASE_URL automatically if you add a PostgreSQL database
        # Fix for SQLAlchemy 1.4+
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to SQLite for local development
        BASE_DIR = Path(__file__).resolve().parent
        DATA_DIR = BASE_DIR / 'data'
        DATA_DIR.mkdir(exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATA_DIR}/janmitra.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ... rest of your config ...
```

---

## Step 3: Deploy to Render

### Option A: Using Render Dashboard (Easiest)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → Select **"Web Service"**
3. **Connect Your GitHub Repository**
4. **Configure the service**:
   - **Name**: `janmitra-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main` or `master`
   - **Root Directory**: `backend` (if your backend is in a folder)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 app:app`

5. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   SECRET_KEY=<generate-a-strong-secret>
   GROQ_API_KEY=<your-groq-key>
   NEWS_API_KEY=<your-news-api-key>
   TWILIO_ACCOUNT_SID=<your-twilio-sid>
   TWILIO_AUTH_TOKEN=<your-twilio-token>
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   CLOUDINARY_CLOUD_NAME=<your-cloudinary-name>
   CLOUDINARY_API_KEY=<your-cloudinary-key>
   CLOUDINARY_API_SECRET=<your-cloudinary-secret>
   DEBUG=False
   ```

6. **(Optional but Recommended) Add PostgreSQL Database**:
   - In your service dashboard, go to "Environment" tab
   - Click "Add Database" → "PostgreSQL"
   - Render will automatically add `DATABASE_URL` environment variable

7. **Click "Create Web Service"**

### Option B: Using render.yaml (Infrastructure as Code)

1. **Copy `render.yaml`** to your repository root (already created)
2. **Push to GitHub**
3. **In Render Dashboard**: 
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect `render.yaml` and deploy

---

## Step 4: Configure WhatsApp Webhook

Once your Render service is deployed:

1. **Get your Render URL**: `https://your-app-name.onrender.com`

2. **Go to Twilio Console**: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox

3. **Set Webhook URL**:
   ```
   https://your-app-name.onrender.com/api/whatsapp/webhook
   ```

4. **Set HTTP Method**: `POST`

5. **Save** and test by sending a message to your Twilio WhatsApp number!

---

## Step 5: Verify Deployment

### Test the API
```bash
# Check if the service is running
curl https://your-app-name.onrender.com/api/stats

# Test WhatsApp webhook (if configured)
curl -X POST https://your-app-name.onrender.com/api/whatsapp/webhook \
  -d "From=whatsapp:+1234567890" \
  -d "Body=Hello JanMitra"
```

### Check Logs
- Go to your Render dashboard
- Click on your service
- Go to "Logs" tab
- You should see:
  ```
  🚀 Starting JanMitra Backend v2.0...
  ⏰ Auto-collection: Every hour
  ```

---

## How Auto Scheduler Works on Render

✅ **Your auto scheduler will work automatically!**

- The `BackgroundScheduler` in `auto_scheduler.py` starts when your app starts
- It runs in the background alongside your Flask app
- Jobs will execute at the configured intervals (every hour for news collection)
- **No additional configuration needed!**

### Monitoring Scheduler Jobs

Check logs to confirm scheduler is working:
```
🔄 Auto-collecting news...
✅ Collected 42 articles
🧠 Auto-processing articles...
```

---

## Important Notes

### 1. **Free Tier Limitations**
- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Scheduled jobs might not run if service is spun down
- **Solution**: Upgrade to paid tier ($7/month) for always-on service

### 2. **Cold Starts**
- WhatsApp users might experience delays on first message
- Consider upgrading to paid tier for better performance

### 3. **Database Persistence**
- **SQLite on Render**: Data is lost on each deploy (not recommended for production)
- **PostgreSQL**: Data persists across deploys (recommended)
- Add PostgreSQL database in Render dashboard (free tier available)

### 4. **CORS Configuration**
Update your `app.py` CORS settings to include your Render URL:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000", 
            "http://localhost:5173",
            "https://your-frontend-domain.com"  # Add your frontend URL
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

---

## Troubleshooting

### Service Won't Start
- Check logs for errors
- Verify all environment variables are set
- Ensure `gunicorn` is in requirements.txt

### WhatsApp Webhook Not Working
- Verify webhook URL is correct in Twilio console
- Check Render logs for incoming requests
- Ensure URL uses HTTPS (Render provides this automatically)

### Scheduler Not Running
- Check if service is spun down (free tier)
- Look for scheduler logs in Render dashboard
- Upgrade to paid tier for always-on service

### Database Errors
- If using SQLite, switch to PostgreSQL for production
- Check DATABASE_URL environment variable
- Verify SQLAlchemy URI format

---

## Deployment Checklist

- [ ] Add `gunicorn` to `requirements.txt`
- [ ] Update `config.py` for PostgreSQL support
- [ ] Push code to GitHub
- [ ] Create Render web service
- [ ] Set all environment variables
- [ ] (Optional) Add PostgreSQL database
- [ ] Deploy and wait for build to complete
- [ ] Copy Render URL
- [ ] Configure Twilio WhatsApp webhook with Render URL
- [ ] Test WhatsApp bot by sending a message
- [ ] Verify auto scheduler in logs
- [ ] Update frontend CORS settings if needed

---

## Summary

🎉 **You're ready to deploy!**

**Key Takeaway**: Ngrok is NOT needed. Render gives you a permanent public URL that works perfectly for WhatsApp webhooks and all other API endpoints.

Your auto scheduler will run automatically in the background, and your WhatsApp bot will be accessible 24/7 (on paid tier) without any tunneling or complex setup.

**Need help?** Check Render docs: https://render.com/docs or Twilio docs: https://www.twilio.com/docs/sms/whatsapp
