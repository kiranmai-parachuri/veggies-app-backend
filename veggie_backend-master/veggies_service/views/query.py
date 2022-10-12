from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.order import OrderView
from veggies_service.views.user import UserBasicView


class OrderQueryView(SchemaRender):
    id = fields.Integer()
    order = fields.Nested(OrderView)
    message = fields.String()
    sender = fields.Nested(UserBasicView)
    receiver = fields.Nested(UserBasicView)
    created_on = DateTimeEpoch()
