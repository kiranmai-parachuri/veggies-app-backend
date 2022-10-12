from veggies_service.db.veggies_models.models import Notification
from veggies_service.utils.exceptions import NotFoundException


def get_notifications_by_filter(filters):
    criteria = {}
    if 'users' in filters:
        criteria['customers__mobile__in'] = filters['users'].split(',')
    return Notification.objects.filter(**criteria)


def get_notification_by_id(id):
    try:
        return Notification.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Notification')


def update_notification(id, data):
    notification = get_notification_by_id(id)
