from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import order_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.order import OrderView


class Order(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.CUSTOMER]:
            raise UnauthorisedException()
        user = get_user_object(token)
        request_data = request.get_json(force=True)
        order_object = order_handler.create_order(request_data, user)
        view = OrderView()
        return {'order': view.render(order_object)}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        request_data = request.get_json(force=True)
        order_object = order_handler.update_order(id, request_data)
        view = OrderView()
        return {'order': view.render(order_object)}

    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        data = request.args
        user = get_user_object(token)
        view = OrderView()
        if get_user_role(token) in [user_role.CUSTOMER]:
            orders_objects, count = order_handler.get_orders_by_filter(data, user)
        else:
            if id:
                order_object = order_handler.get_order_by_id(id)
                return {'order': view.render(order_object)}
            orders_objects, count = order_handler.get_orders_by_filter(data)
        return {'orders': [view.render(order) for order in orders_objects],
                'total': count}
