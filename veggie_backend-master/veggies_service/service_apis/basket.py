from flask import request

from veggies_service.constants import user_role, basket_constants
from veggies_service.service_apis_handler import basket_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.basket import BasketView


class Basket(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        basket = basket_handler.create_basket(request, user)
        view = BasketView()
        return {'basket': view.render(basket)}

    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        view = BasketView()
        if id:
            basket = basket_handler.get_basket_by_id(id)
            return {'basket': view.render(basket)}
        data = request.args
        baskets, count = basket_handler.get_basket_by_filter(data)
        if get_user_role(token) in [user_role.ADMIN]:
            return {'baskets': [view.render(basket) for basket in baskets],
                    'total': count}
        else:
            return {'baskets': [view.render(basket) for basket in
                                filter(lambda x: x.is_one_time_delivery == False, baskets)],
                    'total': count,
                    'oneTimeBasket': [view.render(basket) for basket in
                                      filter(lambda x: x.is_one_time_delivery == True, baskets)],
                    'sections': basket_constants.BASKET_PAGE_DATA, 'image': basket_constants.IMAGE}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        basket = basket_handler.update_basket(id, request)
        view = BasketView()
        return {'basket': view.render(basket)}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        return basket_handler.delete_basket(id)
