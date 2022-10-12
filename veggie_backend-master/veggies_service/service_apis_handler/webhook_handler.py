from django.db import transaction

from veggies_service.constants import payment_constants, order_constants
from veggies_service.db.veggies_models.models import PaymentEvents
from veggies_service.service_apis_handler import order_handler
from veggies_service.utils.email_utils import send_order_placed_email
from veggies_service.utils.fcm.FcmManager import order_placed_notification


@transaction.atomic
def handler_web_hook_events(data):
    order_id = data['payload']['payment']['entity']['order_id']
    payment_id = data['payload']['payment']['entity']['id']
    orders, _ = order_handler.get_orders_by_filter({'orderId': order_id})
    event_type = data['event']
    if orders:
        order = orders[0]
        if event_type == payment_constants.PAYMENT_SUCCESS:
            order.status = payment_constants.SUCCESS
            if order.order_type == order_constants.BASKET:
                order_handler.create_deliveries_for_basket_order(order)
            send_order_placed_email(order)
            order_placed_notification(order.created_by)
        if event_type == payment_constants.PAYMENT_FAILED:
            order.status = payment_constants.FAIL
            order_handler.handle_order_fail(order)
        order.payment_id = payment_id
        order.save()
    return PaymentEvents.objects.create(order=order, info=data, event=event_type)
