from datetime import datetime, timedelta

from veggies_service.constants import delivery_constants
from veggies_service.utils.exceptions import ValidationException


def get_date_time_from_time_stamp(timestamp=""):
    if not timestamp:
        return datetime.now()
    try:
        return datetime.fromtimestamp(int(timestamp) / 1000)
    except:
        raise ValidationException(errorMessage="Invalid datetime format")


def get_customization_end_date(delivery_object):
    date = ((delivery_object.delivery_date - timedelta(delivery_constants.CUSTOMIZATION_END_DELIVERY_DAYS)).replace(
        hour=delivery_constants.CUSTOMIZATION_END_DELIVERY_DAYS_HOUR, minute=0, second=0)) - timedelta(hours=5,
                                                                                                       minutes=30)
    return date


def get_customization_start_date(delivery_object):
    date = ((delivery_object.delivery_date - timedelta(
        delivery_constants.CUSTOMIZATION_START_BEFORE_DELIVERY_DAYS)).replace(
        hour=delivery_constants.CUSTOMIZATION_START_BEFORE_DELIVERY_DAYS_HOUR, minute=0, second=0)) - timedelta(hours=5,
                                                                                                                minutes=30)
    return date


def get_current_date():
    return datetime.now() - timedelta(hours=5,
                                      minutes=30)
