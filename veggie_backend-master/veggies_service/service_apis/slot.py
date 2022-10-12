from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import slot_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.slot import SlotView


class Slot(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        request_data = request.get_json(force=True)
        slot_object = slot_handler.create_slot(request_data, user)
        view = SlotView()
        return {'slot': view.render(slot_object)}

    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        view = SlotView()
        data = request.args
        if id:
            if 'productsEstimate' in data:
                return slot_handler.get_products_quantity_estimate_for_slot(id)
            slot_object = slot_handler.get_slot_by_id(id)
            return {'slot': view.render(slot_object)}
        slot_objects, count = slot_handler.get_slots_by_filter(data)
        return {'slots': [view.render(slot_object) for slot_object in slot_objects], 'total': count}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        return slot_handler.delete_slot(id)
