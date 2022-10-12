from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender
from veggies_service.views.product import ProductView
from veggies_service.views.user import UserBasicView


class FavoriteView(SchemaRender):
    id = fields.Integer()
    user = fields.Nested(UserBasicView)
    product = fields.Nested(ProductView)
