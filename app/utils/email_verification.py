import hashlib # provides fast hashing algos(SHA family, MD5) + salting is done manually
import secrets
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def generate_verification_token():
    return secrets.token_urlsafe(32)

def hash_verification_token(token : str):
    return hashlib.sha256(token.encode()).hexdigest()

def get_verification_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=settings.email_verification_token_expire_minutes)