from marshmallow import fields

from veggies_service.constants.file_constats import SERVER_URL, DOWNLOAD_PATH
from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.user import UserBasicView


class NotificationView(SchemaRender):
    id = fields.Integer()
    label = fields.String()
    customer = fields.Nested(UserBasicView)
    image = fields.Method('get_image_url')
    is_seen = fields.Boolean(dump_to='isSeen')
    created_on = DateTimeEpoch('createdOn')

    def get_image_url(self, obj):
        if obj.image:
            return SERVER_URL + DOWNLOAD_PATH + obj.image
        else:
            return ''
