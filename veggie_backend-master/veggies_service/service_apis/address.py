from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import address_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.address import AddressView


class Address(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.CUSTOMER]:
            raise UnauthorisedException()
        user = get_user_object(token)
        request_data = request.get_json(force=True)
        address_object = address_handler.create_address(request_data, user)
        view = AddressView()
        return {'address': view.render(address_object)}

    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.CUSTOMER]:
            raise UnauthorisedException()
        view = AddressView()
        if id:
            address_object = address_handler.get_address_by_id(id)
            return {'address': view.render(address_object)}
        user = get_user_object(token)
        address_objects = address_handler.get_address_by_filter(user)
        return {'addresses': [view.render(address_object) for address_object in address_objects]}


    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.CUSTOMER]:
            raise UnauthorisedException()
        user = get_user_object(token)
        request_data = request.get_json(force=True)
        address_object = address_handler.update_address(id, request_data, user)
        view = AddressView()
        return {'address': view.render(address_object)}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.CUSTOMER]:
            raise UnauthorisedException()
        return address_handler.delete_address(id)