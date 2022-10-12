from datetime import timedelta

from veggies_service.constants import order_constants, delivery_constants
from veggies_service.db.veggies_models.models import Order
from veggies_service.utils.exceptions import GenericCustomException


def get_delivery_date_for_basket_delivery(user):
    order_with_basket = Order.objects.filter(created_by=user, order_type=order_constants.BASKET).last()
    delivery = order_with_basket.deliveries.filter(status__in=[delivery_constants.SCHEDULED,
                                                               delivery_constants.FREEZE]).first()
    delivery_date = delivery.delivery_date
    return delivery_date


def get_delivery_date_for_order(obj):
    delivery_date = None
    if obj.order_type == order_constants.BASKET:
        delivery_date = get_delivery_date_for_basket_delivery(obj.created_by)
    elif obj.with_basket_delivery:
        delivery_date = get_delivery_date_for_basket_delivery(obj.created_by)
    elif not obj.with_basket_delivery:
        delivery_date = obj.created_on + timedelta(days=obj.address.pincode.delivery_days)
    if delivery_date:
        delivery_date -= timedelta(hours=5,
                                   minutes=30)
        return delivery_date
    else:
        raise GenericCustomException(message='Error while getting delivery date for order')
