from datetime import datetime

import pytz
from django.db import transaction

from veggies_service.constants import user_role
from veggies_service.db.veggies_models.models import Coupon, CouponAvail
from veggies_service.utils.exceptions import BadRequest, NotFoundException, AlreadyExist


@transaction.atomic
def create_coupon(data, user):
    coupon_data = {'user': user}
    try:
        coupon_data['coupon_code'] = data['couponCode']
        coupon_data['apply_count'] = data['applyCount']
        coupon_data['remaining_count'] = data['applyCount']
        coupon_data['price'] = data['price']
        coupon_data['start_time'] = datetime.strptime(data['startTime'], '%d-%m-%Y %H:%M:%S')
        coupon_data['end_time'] = datetime.strptime(data['endTime'], '%d-%m-%Y %H:%M:%S')
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    try:
        coupon = Coupon.objects.create(**coupon_data)
    except:
        raise AlreadyExist(entity='Coupon')
    return coupon


def is_coupon_usable(coupon, user):
    if coupon.remaining_count <= 0:
        return False, 'Coupon expired.'
    if coupon.is_deleted:
        return False, 'Coupon no longer there.'
    local_tz = pytz.timezone('Asia/Kolkata')
    print 'coupon:', coupon.coupon_code
    print 'start: ', coupon.start_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    print 'today: ', datetime.now().replace(
        tzinfo=pytz.utc).astimezone(local_tz)
    print 'end: ', coupon.end_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    if coupon.start_time.replace(tzinfo=pytz.utc).astimezone(local_tz) <= datetime.now().replace(
            tzinfo=pytz.utc).astimezone(local_tz) <= coupon.end_time.replace(tzinfo=pytz.utc).astimezone(local_tz):
        try:
            coupon_avail = get_coupon_avail_for_user_and_coupon(coupon, user)
            if coupon_avail:
                return False, 'You have already used this coupon.'
        except NotFoundException as e:
            return True, 'Coupon is applicable.'
    else:
        return False, 'Coupon expired.'


def apply_coupon(code, user):
    coupon = get_coupon_by_code(code)
    can_apply, message = is_coupon_usable(coupon, user)
    return {'canApply': can_apply, 'message': message, 'price': coupon.price}


@transaction.atomic
def update_coupon(code, data):
    coupon = get_coupon_by_code(code)
    start_time = None
    if 'startTime' in data:
        start_time = datetime.strptime(data['startTime'], '%d-%m-%Y %H:%M:%S')
        if start_time <= datetime.now():
            raise BadRequest(errorMessage='Start time must be greater than current time')
        coupon.start_time = start_time
    if 'endTime' in data:
        end_time = datetime.strptime(data['endTime'], '%d-%m-%Y %H:%M:%S')
        if end_time < datetime.now() or (start_time and start_time > end_time) or coupon.start_time > end_time:
            raise BadRequest(errorMessage='End time must be greater than current time')
        coupon.end_time = end_time
    if 'applyCount' in data:
        if data['applyCount'] < coupon.remaining_count:
            raise BadRequest(errorMessage='Apply count must greater than remaining count')
        else:
            coupon.apply_count = data['applyCount']
            coupon.remaining_count = data['applyCount']
    if 'price' in data:
        coupon.price = data['price']
    if 'isDeleted' in data:
        coupon.is_deleted = data['isDeleted']
    coupon.save()
    coupon.refresh_from_db()
    return coupon


def get_coupons_by_filter(filters={}, user=None):
    criteria = {'is_deleted': False}
    if user:
        if user.role == user_role.ADMIN:
            criteria.pop('is_deleted')
            criteria.update({'is_deleted__in': [True, False]})
    if 'coupon_code' in filters:
        criteria['coupon_code'] = filters['coupon_code']
    return Coupon.objects.filter(**criteria)


def delete_coupon(code):
    coupon = get_coupon_by_code(code)
    coupon.is_deleted = True
    coupon.save()
    coupon.refresh_from_db()
    return coupon


def get_coupon_by_code(code):
    try:
        coupon = Coupon.objects.get(coupon_code=code.upper())
    except Exception as e:
        raise NotFoundException(entity='Coupon')
    return coupon


def get_coupon_avail_for_user_and_coupon(coupon, user):
    try:
        coupon = CouponAvail.objects.get(coupon=coupon, user=user)
        return coupon
    except:
        raise NotFoundException(entity='Coupon Avail')


def create_coupon_avail(coupon, user):
    coupon_avail = CouponAvail.objects.create(coupon=coupon, user=user)
    return coupon_avail
