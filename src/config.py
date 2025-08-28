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

# DB conf
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "monee_flow")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
