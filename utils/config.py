import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),  # no default — force env var
    'database': os.getenv('DB_NAME', 'crm'),
    'port': int(os.getenv('DB_PORT', 3306)),
}

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-not-for-prod')
