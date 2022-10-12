from django.db import transaction

from veggies_service.db.veggies_models.models import DefaultDelivery
from veggies_service.service_apis_handler import order_handler, basket_handler, delivery_handler
from veggies_service.utils.email_utils import send_delivery_customised_email_to_users
from veggies_service.utils.exceptions import BadRequest, NotFoundException


@transaction.atomic
def create_default_delivery(data):
    try:
        order_items = data['orderItems']
        basket_id = data['basket']
    except Exception as e:
        raise BadRequest(errorMessage='Key error: ' + str(e))
    basket_object = basket_handler.get_basket_by_id(id=basket_id)
    items = order_handler.handle_order_items(order_items, is_basket=True)
    used_points = delivery_handler.get_used_points(items)
    delivery_points = basket_object.points / basket_object.deliveries
    if delivery_points < used_points:
        order_items = order_handler.get_order_items_by_filter(
            {'ids': ','.join([str(order_item.id) for order_item in items])})
        order_items.delete()
        raise BadRequest(errorMessage='Requested to be Consumed points should not greater than allowed points.')
    default_delivery = DefaultDelivery.objects.create(points=delivery_points,
                                                      used_points=delivery_handler.get_used_points(items))
    default_delivery.products.add(*items)
    basket_object.default_delivery = default_delivery
    basket_object.save()
    return default_delivery


@transaction.atomic
def apply_default_delivery_to_deliveries(default_delivery, deliveries):
    order_items = default_delivery.products.all()
    used_points = default_delivery.used_points
    users = []
    for delivery in deliveries:
        delivery.products.clear()
        delivery.products.add(*order_items)
        delivery.used_points = used_points
        delivery.is_default_delivery = True
        delivery.save()
        users.append(delivery.user)
    return users


@transaction.atomic
def apply_as_default_delivery_for_freezed_deliveries(id, data):
    delivery = get_delivery_by_id(id)
    if not data.get('basket'):
        raise BadRequest(errorMessage='Please provide Basket')
    basket = basket_handler.get_basket_by_id(data['basket'])
    non_customized_deliveries = delivery_handler.get_freezed_deliveries_for_basket(basket)
    users = apply_default_delivery_to_deliveries(delivery, non_customized_deliveries)
    send_delivery_customised_email_to_users(users, delivery)
    return users


@transaction.atomic
def update_default_delivery(id, data):
    delivery = get_delivery_by_id(id)
    if 'orderItems' in data:
        items = order_handler.handle_order_items(data['orderItems'], is_basket=True)
        used_points = delivery_handler.get_used_points(items)
        if delivery.points < used_points:
            order_items = order_handler.get_order_items_by_filter(
                {'ids': ','.join([str(order_item.id) for order_item in items])})
            order_items.delete()
            raise BadRequest(errorMessage='Requested to be Consumed points should not greater than allowed points.')
        delivery.products.clear()
        delivery.products.add(*items)
        delivery.used_points = delivery_handler.get_used_points(items)
        delivery.save()
        return delivery
    else:
        raise BadRequest(errorMessage='Please provide order items.')


def get_delivery_by_id(id):
    try:
        return DefaultDelivery.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='DefaultDelivery')


def get_deliveries_by_filter(data):
    return DefaultDelivery.objects.all()
