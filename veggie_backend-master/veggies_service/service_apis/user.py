from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import user_handler
from veggies_service.utils.exceptions import AlreadyExist, UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_object, is_logged_in_user_admin, get_user_role, \
    is_logged_in_user_customer
from veggies_service.views.user import UserBasicView


class User(BaseResource):
    def post(self):
        request_data = request.get_json(force=True)
        if 'role' in request_data and request_data['role'] == user_role.ADMIN:
            token = request.headers.get('token')
            if not token:
                token = request.cookies.get('token')
            if not is_logged_in_user_admin(token):
                raise UnauthorisedException()
            if user_handler.is_user_exists(request_data['mobile']):
                raise AlreadyExist(entity='User')
            user_object = user_handler.create_user(request_data, True)
            user_view = UserBasicView()
            return user_view.render(user_object)
        else:
            if 'resend' in request_data:
                user = user_handler.get_user_by_mobile(request_data.get('mobile'))
                user_handler.send_verification_email(user)
                return {'success': True}
            if user_handler.is_user_exists(request_data['mobile']):
                raise AlreadyExist(entity='User')
            else:
                user_object = user_handler.create_user(request_data)
                user_view = UserBasicView()
                return {'user': user_view.render(user_object)}

    def get(self, mobile=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        user_view = UserBasicView()
        if is_logged_in_user_customer(token):
            user_object = get_user_object(token)
            return {'user': user_view.render(user_object)}
        elif is_logged_in_user_admin(token):
            data = request.args
            user_objects, count = user_handler.get_user_by_filter(data)
            return {'users': [user_view.render(user_object) for user_object in user_objects],
                    'total': count}

    def put(self, mobile):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        user = get_user_object(token)
        if not get_user_role(token) in [user_role.CUSTOMER] and user.mobile != mobile:
            raise UnauthorisedException()
        request_data = request.get_json(force=True)
        user_object = user_handler.update_user(request_data, mobile)
        user_view = UserBasicView()
        return {'user': user_view.render(user_object)}
