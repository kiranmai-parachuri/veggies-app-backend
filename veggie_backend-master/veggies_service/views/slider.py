from marshmallow import fields

from veggies_service.constants.file_constats import DOWNLOAD_PATH, SERVER_URL
from veggies_service.views.base_schema import SchemaRender


class SliderView(SchemaRender):
    id = fields.String()
    name = fields.String()
    image = fields.Method('get_image_url')
    image_type = fields.String(dump_to='type')

    def get_image_url(self, obj):
        if obj.image:
            return SERVER_URL + DOWNLOAD_PATH + obj.image
        else:
            return ''
