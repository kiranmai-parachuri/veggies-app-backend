from flask import request

from veggies_service.constants import user_role
from veggies_service.db.veggies_models.models import Favorite as Favorite_Table
from veggies_service.service_apis_handler import product_handler, favorite_handler
from veggies_service.utils.exceptions import UnauthorisedException, BadRequest, NotFoundException, AlreadyExist
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import is_logged_in_user_customer, get_user_object, get_user_role
from veggies_service.views.favorite import FavoriteView


class Favorite(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_customer(token):
            raise UnauthorisedException()
        user = get_user_object(token)
        data = request.get_json(force=True)
        favorite = favorite_handler.create_favorite(data, user)
        view = FavoriteView()
        return {'favorite': view.render(favorite)}

    def get(self, product_id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_customer(token):
            raise UnauthorisedException()
        user = get_user_object(token)
        favorites = favorite_handler.get_favorite_by_filter({'user': user})
        view = FavoriteView()
        return {'favorites': [view.render(f) for f in favorites]}

    def delete(self, product_id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_customer(token):
            raise UnauthorisedException()
        user = get_user_object(token)
        return favorite_handler.delete_favorite(product_id, user)
