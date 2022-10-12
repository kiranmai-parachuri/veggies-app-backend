from uuid import uuid4

from veggies_service.db.veggies_models.models import Login
from veggies_service.utils.exceptions import GenericCustomException


def create_login(user_object, otp_object):
    try:
        login_object = Login.objects.create(user=user_object, otp=otp_object, token=str(uuid4()))
        return login_object
    except Exception as e:
        raise GenericCustomException(message="Error while creating login {}".format(e))


def get_login_user(user_object):
    return Login.objects.filter(user=user_object, is_active=True)
