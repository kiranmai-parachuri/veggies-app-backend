import uuid

from django.db import transaction

from veggies_service.constants import user_role, email_constants, service_constants
from veggies_service.db.veggies_models.models import User
from veggies_service.utils.email_utils import send_email_with_attachments
from veggies_service.utils.exceptions import BadRequest, NotFoundException


def is_user_exists(mobile):
    return User.objects.filter(mobile=mobile)


def is_user_present_for_verification_code(token):
    try:
        return User.objects.get(verification_code=token, is_email_verified=False)
    except:
        return False


def send_verification_email(user):
    url = service_constants.SERVICE_URL + email_constants.EMAIL_VERIFY_END_POINT + '?token=' + user.verification_code
    message = '<h3>Hi ' + user.first_name + ' ' + user.last_name + ',<br><p>' + email_constants.EMAIL_VERIFICATION_MESSAGE + ' <a href=' + url + '>' + url + '</a><h3>'
    send_email_with_attachments(user.email, email_constants.EMAIL_VERIFICATION_SUBJECT, html=message)


@transaction.atomic
def create_user(data, is_admin=None):
    user_data = {}
    try:
        user_data['mobile'] = data['mobile']
    except KeyError as e:
        raise BadRequest(errorMessage="key error:" + str(e))
    if data.get('email'):
        user_data['email'] = data['email']
    if data.get('firstName'):
        user_data['first_name'] = data['firstName']
    if data.get('lastName'):
        user_data['last_name'] = data['lastName']
    if data.get('gender'):
        user_data['gender'] = data['gender']
    if is_admin:
        user_data['role'] = user_role.ADMIN
    user_object = User.objects.create(**user_data)
    user_object.verification_code=str(uuid.uuid4())
    user_object.save()
    user_object.refresh_from_db()
    send_verification_email(user_object)
    # user_object.is_email_verified = True
    user_object.save()
    return user_object


def get_user_by_mobile(mobile):
    try:
        user = User.objects.get(mobile=mobile)
        return user
    except Exception as e:
        raise NotFoundException(entity='User')


def get_user_by_filter(data):
    criteria = {}
    if 'role' in data:
        criteria['role'] = data['role']
    if 'mobile' in data:
        criteria['mobile__in'] = data['mobile'].split(',')
    start_index = end_index = None
    if 'page' in data and 'perPage' in data:
        page = int(data['page'])
        per_page = int(data['perPage'])
        end_index = page*per_page
        start_index = end_index-per_page
    if end_index and not 'q' in data:
        users = User.objects.filter(**criteria)
        return users[start_index:end_index], len(users)
    users = User.objects.filter(**criteria)
    return users, len(users)

def mark_unsubscribed_after_last_delivery(user):
    user.does_hold_membership = False
    user.save()


def does_user_have_membership(user):
    return user.does_hold_membership


def update_user(data, mobile):
    user = get_user_by_mobile(mobile)
    if data.get('email'):
        user.email = data['email']
    if data.get('firstName'):
        user.first_name = data['firstName']
    if data.get('lastName'):
        user.last_name = data['lastName']
    if data.get('gender'):
        user.gender = data['gender']
    if data.get('role'):
        user.role = data['role']
    if 'doesHoldMembership' in data:
        if data['doesHoldMembership']:
            user.does_hold_membership = True
        elif not data['doesHoldMembership']:
            user.does_hold_membership = False
    user.save()
    user.refresh_from_db()
    return user
