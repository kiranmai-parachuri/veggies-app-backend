from flask import request

from veggies_service.constants import user_role, savers_type
from veggies_service.service_apis_handler import saver_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.product import ProductView
from veggies_service.views.saver import SaverView


class Saver(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        request_data = request.get_json(force=True)
        saver = saver_handler.create_saver(request_data, user)
        view = SaverView()
        return {'saver': view.render(saver)}

    def get(self):
        view = SaverView()
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        savers = saver_handler.get_savers()
        user = None
        if token:
            user = get_user_object(token)
        week_savers = savers.filter(saver_type=savers_type.WEEK)
        daily_savers = savers.filter(saver_type=savers_type.DAY)
        week_saver = []
        prod_view = ProductView()
        favorites = {}
        if user:
            favorites = {x.product.id: x for x in user.favorite_set.all()}
        for s in week_savers:
            p_res = prod_view.render(s.product)
            if favorites.get(s.product.id):
                p_res.update({'isFavorite': True})
            else:
                p_res.update({'isFavorite': False})
            s_res = {'id': s.id, 'type': s.saver_type, 'product': p_res}
            week_saver.append(s_res)
        daily_saver = []

        for s in daily_savers:
            p_res = prod_view.render(s.product)
            if favorites.get(s.product.id):
                p_res.update({'isFavorite': True})
            else:
                p_res.update({'isFavorite': False})
            s_res = {'id': s.id, 'type': s.saver_type, 'product': p_res}
            daily_saver.append(s_res)

        return {'savers': {'weekly': week_saver,
                           'daily': daily_saver}}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        return saver_handler.delete_saver(id)
