import time
from datetime import datetime, timedelta

import pytz

from veggies_service.db.veggies_models.models import User
from veggies_service.utils.fcm.FcmManager import marketing_notification


def send_notifications():
    users_to_get_notified = User.objects.filter(does_hold_membership=False).exclude(fcm_id=None)
    users = []
    for user in users_to_get_notified:
        marketing_notification(user)
        users.append(user)
    print 'marketing notification send to: ', [user.first_name + ' ' + user.last_name for user in users]


def send_marketing_notification():
    print 'Marketing notification send started ...'
    local_tz = pytz.timezone('Asia/Kolkata')
    # if for some reason this script is still running
    # after a year, we'll stop after 365 days
    while True:
        # sleep until 3 days
        t = datetime.today().replace(tzinfo=pytz.utc).astimezone(local_tz)
        future = datetime(t.year, t.month, t.day, 8, 0).replace(tzinfo=pytz.utc).astimezone(local_tz)
        if t.hour >= 8:
            send_notifications()
            future += timedelta(days=3)
        time.sleep((future - t).total_seconds())
        print 'Marketing notification sent for: {0}'.format(t.strftime('%d-%m-%Y %H:%M:%S'))


if __name__ == '__main__':
    send_notifications()
