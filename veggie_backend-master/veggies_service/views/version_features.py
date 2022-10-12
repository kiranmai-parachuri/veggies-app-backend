from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender


class Complete(SchemaRender):
    id = fields.String()
    feature = fields.String()
