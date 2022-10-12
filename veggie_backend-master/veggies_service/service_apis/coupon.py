from flask import request

from veggies_service.constants import user_role
from veggies_service.service_apis_handler import coupon_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.coupon import CouponView


class Coupon(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        request_data = request.get_json(force=True)
        coupon = coupon_handler.create_coupon(request_data, user)
        view = CouponView()
        return {'coupon': view.render(coupon)}

    def put(self, code):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        request_data = request.get_json(force=True)
        user = get_user_object(token)
        if 'apply' in request_data:
            return coupon_handler.apply_coupon(code, user)
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        coupon = coupon_handler.update_coupon(code, request_data)
        view = CouponView()
        return {'coupon': view.render(coupon)}

    def get(self, code=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if token:
            user = get_user_object(token)
        view = CouponView()
        user = None
        if code:
            coupon = coupon_handler.get_coupon_by_code(code)
            return {'coupon': view.render(coupon)}
        if user:
            coupons = coupon_handler.get_coupons_by_filter(user=user)
        else:
            coupons = coupon_handler.get_coupons_by_filter()
        return {'coupons': [view.render(coupon) for coupon in coupons]}

    def delete(self, code):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        coupon = coupon_handler.delete_coupon(code)
        view = CouponView()
        return {'coupon': view.render(coupon)}
