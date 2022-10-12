from datetime import time

from veggies_service.constants import delivery_constants
from veggies_service.db.veggies_models.models import Slot
from veggies_service.utils.exceptions import BadRequest, NotFoundException
from veggies_service.views.slot import SlotView


def create_slot(data, user):
    slot_data = {'created_by': user}
    try:
        slot_data['day'] = data['day']
    except Exception as e:
        raise BadRequest(errorMessage='Key error: ' + str(e))
    if 'startTime' in data:
        hour, minute, second = data['startTime'].split(':')
        slot_data['start_time'] = time(int(hour), int(minute), int(second))
    if 'endTime' in data:
        hour, minute, second = data['endTime'].split(':')
        slot_data['end_time'] = time(int(hour), int(minute), int(second))
    return Slot.objects.create(**slot_data)


def get_slot_by_id(id):
    try:
        slot_object = Slot.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Slot')
    return slot_object


def delete_slot(id):
    slot = get_slot_by_id(id)
    if slot.delivery_set.filter().exclude(status__in=[delivery_constants.DELIVERED, delivery_constants.NOT_DELIVERED]):
        raise BadRequest(errorMessage='Slot having active deliveries')
    v = SlotView()
    res = v.render(slot)
    slot.delete()
    return {'slot': res}


def get_products_quantity_estimate_for_slot(id):
    slot = get_slot_by_id(id)
    deliveries = slot.delivery_set.filter(status=delivery_constants.FREEZE)
    order_items = []
    for delivery in deliveries:
        order_items.extend(delivery.extra_products.all())
        order_items.extend(delivery.products.all())
    products_to_quantity = {}

    for order_item in order_items:
        if order_item.product.name in products_to_quantity:
            order_item_quantity = (order_item.quantity.quantity if order_item.quantity.unit in ['KG', 'LTR'] else float(
                order_item.quantity.quantity) / 1000) * order_item.order_quantity
            products_to_quantity[order_item.product.name] = {'quantity': products_to_quantity[order_item.product.name][
                                                                             'quantity'] + order_item_quantity}

        else:
            order_item_quantity = (order_item.quantity.quantity if order_item.quantity.unit in ['KG', 'LTR'] else float(
                order_item.quantity.quantity) / 1000) * order_item.order_quantity
            products_to_quantity[order_item.product.name] = {'quantity': order_item_quantity}
    return products_to_quantity


def get_slots_by_filter(filter={}):
    criteria = {}
    if 'day' in filter:
        criteria['day'] = filter['day']
    if 'ids' in filter:
        criteria['id__in'] = filter['ids'].split(',')
    start_index = end_index = None
    if 'page' in filter and 'perPage' in filter:
        page = int(filter['page'])
        per_page = int(filter['perPage'])
        end_index = page*per_page
        start_index = end_index-per_page
    if end_index:
        slots = Slot.objects.filter(**criteria)
        return slots[start_index:end_index], len(slots)
    slots = Slot.objects.filter(**criteria)
    return slots, len(slots)