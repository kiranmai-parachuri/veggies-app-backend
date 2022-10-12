import time
from datetime import datetime, timedelta

import pytz

from veggies_service.constants import delivery_constants
from veggies_service.db.veggies_models.models import Delivery
from veggies_service.utils import datetime_utils
from veggies_service.utils.fcm.FcmManager import delivery_customise_notification


def send_notifications():
    local_tz = pytz.timezone('Asia/Kolkata')

    current_time = datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
    deliveries = Delivery.objects.filter(status=delivery_constants.SCHEDULED).exclude(user__fcm_id=None)
    users = []
    for delivery in deliveries:
        if current_time > datetime_utils.get_customization_start_date(delivery).replace(tzinfo=pytz.utc).astimezone(
                local_tz) and delivery.status not in [delivery_constants.FREEZE, delivery_constants.DELIVERED,
                                                      delivery_constants.NOT_DELIVERED]:
            delivery_customise_notification(delivery.user, delivery.delivery_date)
            users.append(delivery.user)
    print 'delivery notification send to: ', [user.first_name + ' ' + user.last_name for user in users]


def send_customize_delivery_notification():
    print 'Customize basket notification send started: {0}'.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    local_tz = pytz.timezone('Asia/Kolkata')
    # if for some reason this script is still running
    # after a year, we'll stop after 365 days
    while True:
        # sleep until 8AM
        t = datetime.today().replace(tzinfo=pytz.utc).astimezone(local_tz)
        future = datetime(t.year, t.month, t.day, 8, 0).replace(tzinfo=pytz.utc).astimezone(local_tz)
        if t.hour >= 8:
            send_notifications()
            future += timedelta(days=1)
        time.sleep((future - t).total_seconds())
        print 'Customize basket notification sent for: {0}'.format(t.strftime('%d-%m-%Y %H:%M:%S'))


if __name__ == '__main__':
    send_customize_delivery_notification()
