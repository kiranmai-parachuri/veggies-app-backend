from flask import request

from veggies_service.constants import delivery_constants
from veggies_service.service_apis_handler import default_delivery_handler, basket_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_object, is_logged_in_user_admin
from veggies_service.views.default_delivery import DefaultDeliveryView


class DefaultDelivery(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_admin(token):
            raise UnauthorisedException()
        data = request.get_json(force=True)
        default_delivery = default_delivery_handler.create_default_delivery(data)
        view = DefaultDeliveryView()
        return {'defaultDelivery': view.render(default_delivery)}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_admin(token):
            raise UnauthorisedException()
        user = get_user_object(token)
        data = request.get_json(force=True)
        if 'applyDefault' in data and is_logged_in_user_admin(token):
            users = default_delivery_handler.apply_as_default_delivery_for_freezed_deliveries(id, data)
            if users:
                user_names = ','.join([user.first_name + ' ' + user.last_name + '\n' for user in users])
                return {'message': delivery_constants.DEFAULT_DELIVERY_MSG + user_names}
        default_delivery = default_delivery_handler.update_default_delivery(id, data, user)
        view = DefaultDeliveryView()
        return {'defaultDelivery': view.render(default_delivery)}

    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_admin(token):
            raise UnauthorisedException()
        view = DefaultDeliveryView()
        if id:
            default_delivery = default_delivery_handler.get_delivery_by_id(id)
            return {'defaultDelivery': view.render(default_delivery)}
        data = request.args
        if 'basket' in data:
            basket = basket_handler.get_basket_by_id(data['basket'])
            return {'defaultDelivery': view.render(basket.default_delivery)}
        default_deliveries = default_delivery_handler.get_deliveries_by_filter(data)
        return {'defaultDeliveries': [view.render(default_delivery) for default_delivery in default_deliveries]}
