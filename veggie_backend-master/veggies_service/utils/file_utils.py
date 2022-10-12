import os
import uuid

from werkzeug.utils import secure_filename

from veggies_service.constants.file_constats import UPLOAD_PATH
from veggies_service.utils.exceptions import BadRequest


def delete_file(file_name):
    if os.path.exists(os.path.join(UPLOAD_PATH, file_name)):
        os.remove(os.path.join(UPLOAD_PATH, file_name))
    else:
        print("The file does not exist")


def save_file_base64(file):
    extention = file.split(';')[0].split(':')[1].split('/')[1]
    filename = str(uuid.uuid4()) + '.' + extention
    file = file.partition(",")[2]
    fh = open(os.path.join(UPLOAD_PATH, filename), "wb")
    fh.write(file.decode('base64'))
    fh.close()
    return filename


def save_file(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_PATH, filename))
    return filename


def save_file_from_request(request):
    data = request.form.to_dict()
    if request.files:
        image = request.files['file']
        return save_file(image)
    elif 'file' in data:
        image = data['file']
        return save_file_base64(image)
    else:
        raise BadRequest(errorMessage='Image not provided')


def update_file_from_request(request, entity_object):
    data = request.form.to_dict()
    if request.files:
        image = request.files['file']
        delete_file(entity_object.image)
        return save_file(image)
    elif 'file' in data:
        image = data['file']
        delete_file(entity_object.image)
        return save_file_base64(image)
    else:
        raise BadRequest(errorMessage='Image not provided')
