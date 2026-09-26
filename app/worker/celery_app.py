from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "saas_backend",
    broker = settings.redis_url, # redis is being used as a broker
)