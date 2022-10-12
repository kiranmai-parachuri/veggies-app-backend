from flask import request

from veggies_service.constants import user_role
from veggies_service.db.veggies_models.models import PricePerPoint as PricePerPointModel
from veggies_service.utils.exceptions import UnauthorisedException, BadRequest, NotFoundException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.price_per_point import PricePerPointView


class PricePerPoint(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        data = request.get_json(force=True)
        try:
            price = data['price']
        except KeyError as k:
            raise BadRequest(errorMessage='key error:' + str(k))
        if PricePerPointModel.objects.all():
            raise BadRequest(errorMessage='Object already present please use same')
        price = PricePerPointModel.objects.create(price=price, user=user)
        view = PricePerPointView()
        return {'pricePerPoint': view.render(price)}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        data = request.get_json(force=True)
        try:
            price_object = PricePerPointModel.objects.get(id=id)
        except Exception as e:
            raise NotFoundException(entity='PricePerPointModel')
        if 'price' in data:
            price_object.price = data['price']
        price_object.user = user
        price_object.save()
        price_object.refresh_from_db()
        view = PricePerPointView()
        return {'pricePerPoint': view.render(price_object)}

    def get(self):
        price_object = PricePerPointModel.objects.all().last()
        view = PricePerPointView()
        return {'pricePerPoint': view.render(price_object)}
