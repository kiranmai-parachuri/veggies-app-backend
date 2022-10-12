from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import category_handler
from veggies_service.service_apis_handler.category_handler import get_category_by_id
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import is_logged_in_user_admin, get_user_object, is_logged_in_user_customer, \
    get_user_role
from veggies_service.views.category import CategoryView


class Category(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        category = category_handler.create_category(request, user)
        view = CategoryView()
        return {'category': view.render(category)}

    def get(self, id=None):
        if id:
            category = get_category_by_id(id)
            view = CategoryView()
            return {'category': view.render(category)}
        categories = category_handler.get_categories()
        view = CategoryView()
        return {'categories': [view.render(category) for category in categories]}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        category = category_handler.update_category(id, request)
        view = CategoryView()
        return {'category': view.render(category)}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_admin(token):
            raise UnauthorisedException()
        return category_handler.delete_category(id)
