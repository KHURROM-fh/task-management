from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task, Notification
from datetime import date
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def check_due_dates(self):
    logger.info("Task Start...........")
    print("Task Start...........")

    try:
        tasks = Task.objects.filter(due_date__lt=date.today(), is_notified=False, is_completed=False)
        channel_layer = get_channel_layer()
        
        for task in tasks:
            notification = Notification.objects.create(user=task.user, task=task, type="End")

            async_to_sync(channel_layer.group_send)(
                f"user_{task.user.id}",  # Group name fix
                {
                    'type': 'send.notification',
                    'message': notification.full_message(),
                    'task': task.title,
                }
            )

            task.is_notified = True
            task.save()

        logger.info("Task Completed Successfully")
        return "Done"
    except Exception as e:
        logger.error(f"Error in check_due_dates: {e}")
        return "Error"


@shared_task(bind=True)
def test_task(self):
    for i in range(10):
        print(i)
    return "Done"
