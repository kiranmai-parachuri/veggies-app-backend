from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.user import UserBasicView


class PricePerPointView(SchemaRender):
    id = fields.Integer()
    price = fields.Float()
    updated_on = DateTimeEpoch(dump_to='updatedOn')
    user = fields.Nested(UserBasicView)
