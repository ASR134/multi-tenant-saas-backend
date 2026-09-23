import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from app.core.config import settings


def generate_password_reset_token():
    return secrets.token_urlsafe(32)


def hash_password_reset_token(token : str):
    return hashlib.sha256(token.encode()).hexdigest()


def get_password_reset_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_expire_minutes)