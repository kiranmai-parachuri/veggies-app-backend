import json

from flask import make_response

from veggies_service.constants.sms_service_constans import SEND_SMS
from veggies_service.db.veggies_models.models import OTP, Login, User
from veggies_service.service_apis_handler.login_handler import create_login, get_login_user
from veggies_service.utils.exceptions import UnauthorisedException, NotFoundException
from veggies_service.utils.sms_utils import generate_otp, send_otp_msg91


def handle_logout(token):
    login_object = get_login_by_token(token)
    login_object.is_active = False
    login_object.save()
    res = {"status": True,
           "message": "Operation successful",
           "requestData": {}}
    response = make_response(json.dumps(res, indent=4), 200)
    response.mimetype = 'application/json'
    response.set_cookie("token", '')
    return response


def handle_resend_otp(token):
    return True


def verify_and_send_otp(data):
    mobile = data['mobile']
    try:
        user_object = User.objects.get(mobile=mobile)
    except Exception as e:
        raise NotFoundException(entity='User')
    otp = generate_otp()
    if SEND_SMS == 'False':
        otp = OTP.objects.create(user=user_object, otp=otp, request_id="2122")
        return True
    request_id = send_otp_msg91(mobile, otp)
    if request_id:
        otp = OTP.objects.create(user=user_object, otp=otp, request_id=request_id)
        return True


def get_login_by_token(token):
    try:
        login_object = Login.objects.get(token=token)
        return login_object
    except Exception as e:
        raise NotFoundException(entity='Login')


def get_user_for_otp(data):
    try:
        req_otp = data['otp']
        mobile = data['mobile']
    except KeyError:
        raise KeyError
    try:
        user_object = User.objects.get(mobile=mobile)
    except Exception as e:
        raise UnauthorisedException()
    if 'fcmId' in data:
        user_object.fcm_id=data['fcmId']
        user_object.save()
        user_object.refresh_from_db()
    otp_object = user_object.otp_set.last()
    if otp_object.otp != req_otp:
        raise UnauthorisedException()
    else:
        login_object = get_login_user(user_object).first()
        if login_object:
            return login_object
        else:
            login_object = create_login(user_object, otp_object)
            return login_object
