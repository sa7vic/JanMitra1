import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'janmitra-dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # Use PostgreSQL in production (Render), SQLite in development
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        # Fix for SQLAlchemy 1.4+ (Render uses postgres:// but SQLAlchemy needs postgresql://)
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to SQLite for local development
        DATA_DIR.mkdir(exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATA_DIR}/janmitra.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

    # File upload limits
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', 5))
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'heic'}
    
    SCRAPE_INTERVAL_HOURS = 1
    MAX_ARTICLES_PER_SOURCE = 10
    
    AI_MODEL = 'llama-3.3-70b-versatile'
    MAX_TOKENS = 1024
    TEMPERATURE = 0.7

# Create data directory only if it doesn't exist (for local SQLite)
if not os.getenv('DATABASE_URL'):
    DATA_DIR.mkdir(exist_ok=True)