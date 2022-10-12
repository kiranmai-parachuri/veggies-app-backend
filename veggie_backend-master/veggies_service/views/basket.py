from marshmallow import fields

from veggies_service.constants.file_constats import SERVER_URL, DOWNLOAD_PATH
from veggies_service.utils.string_utils import string_unmarshal
from veggies_service.views.base_schema import SchemaRender
from veggies_service.views.default_delivery import DefaultDeliveryView
from veggies_service.views.product import ProductView


class BasketView(SchemaRender):
    id = fields.Integer()
    name = fields.String()
    image = fields.Method('get_image_url')
    points = fields.Integer()
    price = fields.Float()
    deliveries = fields.Integer()
    show = fields.Boolean()
    description = fields.Method('get_description')
    products = fields.Method('get_products')
    default_delivery = fields.Nested(DefaultDeliveryView)
    is_one_time_delivery = fields.Boolean(dump_to='isOneTimeDelivery')

    def get_products(self, obj):
        view = ProductView()
        products = obj.products.all()
        return [view.render(product) for product in products]

    def get_image_url(self, obj):
        if obj.image:
            return SERVER_URL + DOWNLOAD_PATH + obj.image
        else:
            return ''

    def get_description(self, obj):
        return string_unmarshal(obj.description)


if __name__ == '__main__':
    import django;

    django.setup()
    from veggies_service.db.veggies_models.models import Basket

    o = Basket.objects.first()
    v = BasketView()
    print v.render(o)
