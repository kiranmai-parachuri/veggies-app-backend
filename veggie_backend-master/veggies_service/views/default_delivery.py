from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.order_item import OrderItemView


class DefaultDeliveryView(SchemaRender):
    id = fields.Integer()
    points = fields.Integer()
    used_points = fields.Integer(dump_to='usedPoints')
    products = fields.Method('get_products')
    created_on = DateTimeEpoch(dump_to='createdOn')

    def get_products(self, obj):
        products = obj.products.all()
        v = OrderItemView()
        return [v.render(product) for product in products]
