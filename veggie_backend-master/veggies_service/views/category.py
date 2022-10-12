from marshmallow import fields

from veggies_service.constants.file_constats import DOWNLOAD_PATH, SERVER_URL
from veggies_service.views.base_schema import SchemaRender


class CategoryView(SchemaRender):
    id = fields.Integer()
    name = fields.String()
    image = fields.Method('get_image_url')

    def get_image_url(self, obj):
        if obj.image:
            return SERVER_URL + DOWNLOAD_PATH + obj.image
        else:
            return ''
