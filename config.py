import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config(object):
    DEBUG = os.getenv("DEBUG", "False") == "True"
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES"))
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # OOTD
    OOTD_PARAM_STEPS = int(os.getenv("OOTD_PARAM_STEPS"))
    OOTD_PARAM_GUIDANCE_SCALE = float(os.getenv("OOTD_PARAM_GUIDANCE_SCALE"))
    OOTD_PARAM_SEED = int(os.getenv("OOTD_PARAM_SEED"))
    OOTD_PARAM_API_NAME = os.getenv("OOTD_PARAM_API_NAME")
    # Hugging Face token for the OOTDiffusion Space. Optional: without it the
    # Space is called anonymously (lower queue priority, tighter rate limits).
    HF_TOKEN = os.getenv("HF_TOKEN") or None
    # Which try-on Space to call: "ootd" (default) or "catvton".
    TRYON_BACKEND = os.getenv("TRYON_BACKEND") or "ootd"
    # Origin used to build public /static/ URLs. Empty -> taken from the
    # incoming request, which is right behind nginx.
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL") or None

    # AWS Bucket
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
    AWS_S3_BUCKET_URL = os.getenv("AWS_S3_BUCKET_URL")

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    # Exchange Rate API : https://www.exchangerate-api.com/
    EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
