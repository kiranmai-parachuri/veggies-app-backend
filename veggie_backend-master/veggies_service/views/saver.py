from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender
from veggies_service.views.product import ProductView


class SaverView(SchemaRender):
    id = fields.Integer()
    saver_type = fields.String('type')
    product = fields.Nested(ProductView)
