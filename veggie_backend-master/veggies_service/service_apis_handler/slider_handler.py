import os

from veggies_service.constants.file_constats import UPLOAD_PATH
from veggies_service.db.veggies_models.models import Image
from veggies_service.utils.exceptions import BadRequest, NotFoundException
from veggies_service.utils.file_utils import save_file, save_file_base64, delete_file, update_file_from_request, \
    save_file_from_request
from veggies_service.views.slider import SliderView


def create_slider_image(request, user):
    data = request.form.to_dict()
    image_data = {'created_by': user}
    try:
        image_data['name'] = data['name']
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    if 'type' in data:
        image_data['image_type'] = data['type']
    image_data['image'] = save_file_from_request(request)
    image = Image.objects.create(**image_data)
    return image


def get_slider_images():
    return Image.objects.all()


def get_slider_image_by_id(id):
    try:
        slider = Image.objects.get(id=id)
        return slider
    except Exception as e:
        raise NotFoundException(entity='Slider')


def update_slider(id, request):
    slider = get_slider_image_by_id(id)
    data = request.form.to_dict()
    if request.files or 'file' in data:
        slider.image = update_file_from_request(request, slider)
    if 'type' in data:
        slider.image_type = data['type']
    if 'name' in data:
        slider.name = data['name']
    slider.save()
    slider.refresh_from_db()
    return slider


def delete_slider(id):
    slider = get_slider_image_by_id(id)
    view = SliderView()
    res = view.render(slider)
    delete_file(slider.image)
    slider.delete()
    return res
