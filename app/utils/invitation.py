import secrets
import hashlib

from datetime import datetime, timezone, timedelta
from app.core.config import settings

def generate_invitation_token():
    return secrets.token_urlsafe(32)


def hash_invitation_token(token : str):
    return hashlib.sha256(token.encode()).hexdigest()


def get_invitation_expiry():
    return datetime.now(timezone.utc) + timedelta(days=settings.invitation_token_expire_days)