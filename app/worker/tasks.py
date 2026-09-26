from app.worker.celery_app import celery_app
from app.services.email import EmailService
import logging
import asyncio

logger = logging.getLogger(__name__)


@celery_app.task(bind=True,max_retries=3) # this tells celery that this function is a task, worker can execute
def send_invitation_accepted_notification(
    self,
    inviter_email : str,
    invitee_email : str,
    organization_name : str,
):

    email_service = EmailService()

    try : 
        asyncio.run(email_service.send_invitation_accepted_notification(
                inviter_email=inviter_email,
                invitee_email = invitee_email,
                organization_name=organization_name,
            )
        )
    except Exception as exc:
        logger.warning(
            "Invitation acceptance notification failed. Retrying..."
        )
        raise self.retry(exc=exc, countdown = 5)