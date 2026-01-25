import os
from dotenv import load_dotenv

# Load .env
ENV = os.getenv("ENVIRONMENT", "development")
if ENV == "test":
    load_dotenv(".env.test")
elif ENV == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env")  # Default=dev

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "monee_flow")

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Open Exchange Rates app_id
OER_APP_ID = os.getenv("OER_APP_ID", "")
OER_BASE_URL = os.getenv("OER_BASE_URL", "")
