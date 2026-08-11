import os

from dotenv import load_dotenv


load_dotenv()


APP_NAME = os.getenv(
    "APP_NAME",
    "AI Resume Intelligence"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY is not configured"
    )


EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "paraphrase-MiniLM-L3-v2"
)

EMBEDDING_BATCH_SIZE = int(
    os.getenv(
        "EMBEDDING_BATCH_SIZE",
        "16"
    )
)

RAG_CHUNK_SIZE = int(
    os.getenv(
        "RAG_CHUNK_SIZE",
        "1000"
    )
)

RAG_CHUNK_OVERLAP = int(
    os.getenv(
        "RAG_CHUNK_OVERLAP",
        "150"
    )
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )
)

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "10")
)
PASSWORD_RESET_OTP_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_OTP_EXPIRE_MINUTES", "10")
)
PASSWORD_RESET_MAX_ATTEMPTS = int(
    os.getenv("PASSWORD_RESET_MAX_ATTEMPTS", "5")
)
PASSWORD_RESET_REQUEST_LIMIT = int(
    os.getenv("PASSWORD_RESET_REQUEST_LIMIT", "3")
)
PASSWORD_RESET_REQUEST_WINDOW_MINUTES = int(
    os.getenv("PASSWORD_RESET_REQUEST_WINDOW_MINUTES", "15")
)

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "console"
).strip().lower()
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
SMTP_USE_TLS = os.getenv(
    "SMTP_USE_TLS",
    "true"
).lower() == "true"
SMTP_TIMEOUT_SECONDS = int(
    os.getenv("SMTP_TIMEOUT_SECONDS", "10")
)

GCS_BUCKET_NAME = os.getenv(
    "GCS_BUCKET_NAME"
)

GCS_KEY_PREFIX = os.getenv(
    "GCS_KEY_PREFIX",
    "resumes"
)

GCP_PROJECT_ID = os.getenv(
    "GCP_PROJECT_ID"
)

PUBSUB_RESUME_PROCESSING_TOPIC = os.getenv(
    "PUBSUB_RESUME_PROCESSING_TOPIC"
)
