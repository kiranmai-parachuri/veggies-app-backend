from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender


class SlotView(SchemaRender):
    id = fields.Integer()
    day = fields.Integer()
    start_time = fields.String()
    end_time = fields.String()

