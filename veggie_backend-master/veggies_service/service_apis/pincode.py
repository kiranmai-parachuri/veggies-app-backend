from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import pincode_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.pincode import PincodeView


class Pincode(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        request_data = request.get_json(force=True)
        pincode = pincode_handler.create_pincode(request_data, user)
        view = PincodeView()
        return {'pincode': view.render(pincode)}

    def get(self, id=None):
        view = PincodeView()
        if id:
            pincode = pincode_handler.get_pincode_by_id(id)
            return {'pincode': view.render(pincode)}
        pincodes = pincode_handler.get_pincodes()
        return {'pincodes': [view.render(pincode) for pincode in pincodes]}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        request_data = request.get_json(force=True)
        pincode = pincode_handler.update_pincode(id, request_data)
        view = PincodeView()
        return {'pincode': view.render(pincode)}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        return pincode_handler.delete_pincode(id)
