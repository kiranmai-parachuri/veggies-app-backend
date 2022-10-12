from flask import request

from veggies_service.service_apis_handler import webhook_handler
from veggies_service.utils.resource import BaseResource


class Webhook(BaseResource):
    def post(self):
        data = request.get_json(force=True)
        webhook_handler.handler_web_hook_events(data)
        return {'success': True}
