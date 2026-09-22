from fastapi import HTTPException, status
from app.db.redis import redis_client
from app.core.config import settings

EMAIL_IP_LIMIT = settings.login_email_ip_limit
IP_LIMIT = settings.login_ip_limit
WINDOW = settings.login_window

async def check_login_rate_limit(
        email : str,
        ip : str,
):
    email = email.lower().strip()

    email_ip_key = f"login:fail:{ip}:{email}"
    ip_key = f"login:fail:ip:{ip}"

    email_ip_attempts = await redis_client.get(email_ip_key)
    ip_attempts = await redis_client.get(ip_key)

    if email_ip_attempts and int(email_ip_attempts) >= EMAIL_IP_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )

    if ip_attempts and int(ip_attempts) >= IP_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )


async def record_failed_login(
        email : str,
        ip : str,
):
    email = email.lower().strip()

    email_ip_key = f"login:fail:{ip}:{email}"
    ip_key = f"login:fail:ip:{ip}"

    email_ip_attempts = await redis_client.incr(email_ip_key)
    ip_attempts = await redis_client.incr(ip_key)

    if email_ip_attempts == 1:
        await redis_client.expire(email_ip_key,WINDOW)

    if ip_attempts == 1:
        await redis_client.expire(ip_key,WINDOW)


async def reset_login_attempts(
        email : str,
        ip : str,
):
    email = email.lower().strip()

    email_ip_key = f"login:fail:{ip}:{email}"

    await redis_client.delete(email_ip_key)