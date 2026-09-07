from app.worker.celery_app import celery_app

@celery_app.task(bind=True,max_retries=3) # this tells celery that this function is a task, worker can execute
def send_invitation_notification(self,invitation_id:int):

    try : 
        print(f"Sending notification for invitation {invitation_id}")
        
        # stimulate sending notification
        print("Invitation notification sent sucessfully!")

    except Exception as exc:
        print("Notification failed. Retrying...")
        raise self.retry(exc=exc, countdown = 5)