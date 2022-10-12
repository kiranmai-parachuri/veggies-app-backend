from flask import request

from veggies_service.constants import user_role, image_type_constants
from veggies_service.service_apis_handler import slider_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import get_user_role, get_user_object
from veggies_service.views.slider import SliderView


class Slider(BaseResource):
    def post(self):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        user = get_user_object(token)
        slider = slider_handler.create_slider_image(request, user)
        view = SliderView()
        return {'slider': view.render(slider)}

    def get(self):
        images = slider_handler.get_slider_images()
        sliders = images.filter(image_type=image_type_constants.SLIDER)
        banners = images.filter(image_type=image_type_constants.BANNER)
        view = SliderView()
        return {"sliders": [view.render(slider) for slider in sliders],
                'banners': [view.render(banner) for banner in banners]}

    def put(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        slider = slider_handler.update_slider(id, request)
        view = SliderView()
        return {'slider': view.render(slider)}

    def delete(self, id):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if not get_user_role(token) in [user_role.ADMIN]:
            raise UnauthorisedException()
        return {'slider': slider_handler.delete_slider(id)}
