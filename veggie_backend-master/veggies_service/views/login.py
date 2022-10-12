from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender
from veggies_service.views.user import UserBasicView


class LoginView(SchemaRender):
    user = fields.Nested(UserBasicView)
    token = fields.String()


if __name__ == '__main__':
    pass