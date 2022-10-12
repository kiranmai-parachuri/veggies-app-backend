from flask import request

from veggies_service.service_apis_handler import product_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import is_logged_in_user_admin, get_user_object
from veggies_service.views.product import ProductView


class Product(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_admin(token):
            raise UnauthorisedException()
        user = get_user_object(token)
        product_object = product_handler.create_product(request, user)
        view = ProductView()
        return {'product': view.render(product_object)}

    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        favorites = {}
        user = None
        if token:
            user = get_user_object(token)
            favorites = {x.product.id: x for x in user.favorite_set.all()}
        view = ProductView()
        if id:
            product = product_handler.get_product_by_id(id)
            return {'product': view.render(product)}
        data = request.args
        if user:
            product_objects, count = product_handler.get_products_by_filter(data, user)
        else:
            product_objects, count = product_handler.get_products_by_filter(data)
        res = []
        for product in product_objects:
            prod_res = view.render(product)
            if favorites.get(product.id):
                prod_res.update({'isFavorite': True})
            else:
                prod_res.update({'isFavorite': False})
            res.append(prod_res)
        return {'products': res, 'total': count}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_admin(token):
            raise UnauthorisedException()
        product_object = product_handler.update_product(request, id)
        view = ProductView()
        return {'products': view.render(product_object)}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not is_logged_in_user_admin(token):
            raise UnauthorisedException()
        return {'products': product_handler.delete_product(id)}
