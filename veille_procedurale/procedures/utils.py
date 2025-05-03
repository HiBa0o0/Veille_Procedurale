from django.utils import timezone
from .models import ProcedureNotification

def send_procedure_notification(procedure, users, notification_type, message):
    """
    Send notifications to users about a procedure
    Args:
        procedure: Procedure instance
        users: QuerySet or list of User instances
        notification_type: 'new' or 'update'
        message: Notification message
    """
    notifications = []
    for user in users:
        notification = ProcedureNotification(
            user=user,
            procedure=procedure,
            notification_type=notification_type,
            message=message,
            is_read=False
        )
        notifications.append(notification)
    
    if notifications:
        ProcedureNotification.objects.bulk_create(notifications)