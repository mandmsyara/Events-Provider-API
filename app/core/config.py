import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DATABASE_NAME")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# DATABASE_URL = os.getenv(
#     "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/events_db"
# )

EXTERNAL_API_KEY = os.getenv("X_API_KEY")
EXTERNAL_API_URL = (
    "http://student-system-events-provider-web.student-system-events-provider.svc:8000/"
)
