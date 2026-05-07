# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "default-secret-key-change-in-production")
    
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    # DB Path
    DB_PATH = 'data/users.db'