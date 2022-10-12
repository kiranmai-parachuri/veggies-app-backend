from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import notification_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.notification import NotificationView


class Notification(BaseResource):
    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN, user_role.CUSTOMER]:
            raise UnauthorisedException()
        user = get_user_object(token)
        if user.role == user_role.CUSTOMER:
            notifications = notification_handler.get_notifications_by_filter(user)
        view = NotificationView()
        return {'notifications': [view.render(notification) for notification in notifications]}
