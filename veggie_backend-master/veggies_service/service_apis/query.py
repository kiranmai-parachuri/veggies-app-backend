from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import query_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object, is_logged_in_user_admin
from veggies_service.views.order import OrderView
from veggies_service.views.query import OrderQueryView


class Query(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN, user_role.CUSTOMER]:
            raise UnauthorisedException()
        request_data = request.get_json(force=True)
        user = get_user_object(token)
        query = query_handler.create_query(request_data, user)
        view = OrderQueryView()
        res = {'query': view.render(query)}
        return res

    def get(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN, user_role.CUSTOMER]:
            raise UnauthorisedException()
        user = get_user_object(token)
        data = request.args
        if is_logged_in_user_admin(token) and not data.get('orderId'):
            orders_with_queries = query_handler.get_order_with_new_queries_for_admin(user)
            order_view = OrderView()
            res_with_query = [{'order': order_view.render(o.order), 'isNewQuery': True} for o
                              in orders_with_queries]
            orders_without_query = query_handler.get_read_orders_for_admin(user)
            res_without_query = [{'order': order_view.render(o.order), 'isNewQuery': False} for o
                                 in orders_without_query]
            res_with_query.extend(res_without_query)
            return res_with_query
        queries = query_handler.get_queries_by_filter(data, user)
        view = OrderQueryView()
        res = {'queries': [view.render(query) for query in queries]}
        if is_logged_in_user_admin(token) and data.get('orderId'):
            query_handler.mark_query_read(queries, user)
        return res
