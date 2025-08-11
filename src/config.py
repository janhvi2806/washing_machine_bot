import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Bot Token
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Google Gemini API Key (REPLACED OpenAI)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Mantis Hub Configuration
    MANTIS_BASE_URL = os.getenv('MANTIS_BASE_URL')
    MANTIS_API_TOKEN = os.getenv('MANTIS_API_TOKEN')
    MANTIS_USERNAME = os.getenv('MANTIS_USERNAME')
    MANTIS_PASSWORD = os.getenv('MANTIS_PASSWORD')
    MANTIS_PROJECT_ID = os.getenv('MANTIS_PROJECT_ID', '1')
    
    # Bot Configuration
    COMMAND_PREFIX = '!'
    SUPPORT_CHANNEL_ID = int(os.getenv('SUPPORT_CHANNEL_ID', '0'))
    
    # Database
    DATABASE_PATH = 'bot_database.db'
