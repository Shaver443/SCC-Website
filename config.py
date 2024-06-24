from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.urandom(32)
    TURNSTILE_SECRET_KEY = os.getenv('TURNSTILE_SECRET_KEY')
    POSTMARK_API_KEY = os.getenv('POSTMARK_API_KEY')
    POSTMARK_SENDER = os.getenv('POSTMARK_SENDER')
