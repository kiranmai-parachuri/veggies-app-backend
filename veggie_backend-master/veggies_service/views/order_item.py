from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.product import ProductView, QuantityView


class OrderItemView(SchemaRender):
    id = fields.Integer()
    product = fields.Nested(ProductView)
    quantity = fields.Nested(QuantityView)
    order_quantity = fields.Integer(dump_to='orderQuantity')
    amount = fields.Float()
    created_on = DateTimeEpoch(dump_to='createdOn')
