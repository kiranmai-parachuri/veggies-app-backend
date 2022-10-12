import os
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, messaging

# import django;
# django.setup()
from veggies_service.constants.push_notification import ENABLE_NOTIFICATION

current_dir_path = os.path.dirname(os.path.realpath(__file__))
cred = credentials.Certificate(
    current_dir_path + "/kmnaturals-4eda2-firebase-adminsdk-lc18a-56b356ff09.json")
firebase_admin.initialize_app(cred)

ORDER = 'ORDER'
DELIVERY = 'DELIVERY'
HOME = 'HOME'


def order_placed_notification(user):
    fcm_id = user.fcm_id

    send_multicast([fcm_id], "Order Placed", "Dear Customer, Your order placed successfully.", ORDER)


def order_delivered_notification(user):
    fcm_id = user.fcm_id

    send_multicast([fcm_id], "Order Delivered", "Dear Customer, Your order delivered successfully.", ORDER)


def delivery_customise_notification(user, delivery_date):
    fcm_id = user.fcm_id
    # fcm_id='dh-kANaYRQeYH-4kGg8Kwy:APA91bFJBnw7f_pZgV2WGeLo-WT_VbnTDO27a138cgK1gsiXIq_CQ3ew3_FFM3m4vqFhE_rtLtAgjnxbK41Jxb85h4RqzJxwl2hGsgAPArxDLwxyXq_5ry9cs_kEdfJo1eNY3XjJd35r'
    send_multicast([fcm_id], "Customize Delivery",
                   "Dear Customer, HURRY UP!!! Please customize your basket today before 10 PM for delivery scheduled on {0}.".format(
                       delivery_date.strftime('%dth %b')),
                   DELIVERY)


def marketing_notification(user):
    fcm_id = user.fcm_id
    send_multicast([fcm_id], "Place your order.",
                   "Dear Customer, Please place your order to get your fresh vegetable and daily needs.", HOME)


def send_multicast(registration_tokens, title, body, screen):
    if not ENABLE_NOTIFICATION:
        print 'Push notification not enabled'
        return True
    try:
        if registration_tokens is None:
            registration_tokens = []
        if not registration_tokens:
            print 'registration token not provided'
            return
        message = messaging.MulticastMessage(
            data={'screen': screen, 'click_action': 'FLUTTER_NOTIFICATION_CLICK'},
            # screen=  ORDER or DELIVERY or HOME
            # data,
            tokens=registration_tokens,
            # notification=messaging.Notification(title="Hello", body="How are you")
            notification=messaging.Notification(title=title, body=body)
        )
        response = messaging.send_multicast(message)
        print('{0} messages were sent successfully to: {1} for: {2}'.format(response.success_count,
                                                                            registration_tokens[0],
                                                                            screen))
    except Exception as e:
        print "error while sending notitfication: {0}".format(str(e))


if __name__ == '__main__':
    from veggies_service.db.veggies_models.models import User

    u = User.objects.get(mobile=312312123)
    # marketing_notification(u)
    delivery_customise_notification(u, datetime.now())
    # order_delivered_notification(u)
    # marketing_notification(u)
