from datetime import datetime

import pytz
from django.db import transaction
from flask import make_response

from veggies_service.constants import delivery_constants, google_map_constant
from veggies_service.db.veggies_models.models import Delivery
from veggies_service.service_apis_handler import order_handler, user_handler
from veggies_service.utils import datetime_utils
from veggies_service.utils.exceptions import NotFoundException, BadRequest
from veggies_service.utils.pdf_utils import MyFPDF


def get_deliveries_by_filter(filter):
    criteria = {}
    if 'ids' in filter:
        criteria['id__in'] = filter['ids'].split(',')
    if 'user' in filter:
        criteria['user_id'] = filter['user']
    if 'status' in filter:
        criteria['status__in'] = filter['status'].split(',')
    if 'slot' in filter:
        criteria['slot'] = filter['slot']
    if 'unCustomised' in filter:
        criteria['products'] = None
        criteria['status'] = delivery_constants.FREEZE
    start_index = end_index = None
    if 'page' in filter and 'perPage' in filter:
        page = int(filter['page'])
        per_page = int(filter['perPage'])
        end_index = page * per_page
        start_index = end_index - per_page
    if end_index:
        deliveries = Delivery.objects.filter(**criteria)
        return deliveries[start_index:end_index], len(deliveries)
    deliveries = Delivery.objects.filter(**criteria)
    return deliveries, len(deliveries)


def get_delivery_by_id(id):
    try:
        delivery = Delivery.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Delivery')
    return delivery


def mark_delivery_editable_if_customization_start(deliveries):
    local_tz = pytz.timezone('Asia/Kolkata')

    current_time = datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
    for delivery in deliveries:
        if current_time > datetime_utils.get_customization_start_date(delivery).replace(tzinfo=pytz.utc).astimezone(
                local_tz) and delivery.status not in [delivery_constants.FREEZE, delivery_constants.DELIVERED,
                                                      delivery_constants.NOT_DELIVERED]:
            delivery.status = delivery_constants.EDITABLE
            delivery.save()


def mark_delivery_freeze_if_customization_end(deliveries):
    local_tz = pytz.timezone('Asia/Kolkata')

    current_time = datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
    for delivery in deliveries:
        if current_time > datetime_utils.get_customization_end_date(delivery).replace(tzinfo=pytz.utc).astimezone(
                local_tz) and delivery.status not in [delivery_constants.FREEZE, delivery_constants.DELIVERED,
                                                      delivery_constants.NOT_DELIVERED]:
            delivery.status = delivery_constants.FREEZE
            delivery.save()


@transaction.atomic
def get_freezed_deliveries_for_basket(basket):
    deliveries = basket.delivery_set.filter(status=delivery_constants.FREEZE)
    return deliveries


def is_delivery_editable(delivery):
    local_tz = pytz.timezone('Asia/Kolkata')

    current_time = datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
    return datetime_utils.get_customization_start_date(delivery).replace(tzinfo=pytz.utc).astimezone(
        local_tz) <= current_time >= datetime_utils.get_customization_end_date(delivery).replace(
        tzinfo=pytz.utc).astimezone(
        local_tz)


def get_used_points(order_items):
    used_points = 0
    for order_item in order_items:
        used_points += int(order_item.product.plan_details.price) * order_item.order_quantity
    return used_points


status_transition = {
    (delivery_constants.FREEZE, delivery_constants.DELIVERED): True,
    (delivery_constants.FREEZE, delivery_constants.NOT_DELIVERED): True,
}


@transaction.atomic
def update_delivery(id, data, user):
    if id:
        delivery = get_delivery_by_id(id)
    # if not is_delivery_editable(delivery) and user.role == user_role.CUSTOMER:
    #     raise GenericCustomException(message='Can not edit delivery as customization time over !!')

    if 'orderItems' in data:
        items = order_handler.handle_order_items(data['orderItems'], is_basket=True)
        delivery.products.clear()
        delivery.products.add(*items)
        to_be_used_points = get_used_points(items)
        if delivery.is_extra_paid_delivery and to_be_used_points < delivery.used_points:
            raise BadRequest(errorMessage='Extra Paid delivery can not be customize below consumed points.')
        if to_be_used_points > delivery.used_points and not delivery.is_extra_paid_delivery:
            delivery.is_extra_paid_delivery = True
        delivery.used_points = to_be_used_points
    if 'status' in data:
        if data['status'] in [delivery_constants.DELIVERED, delivery_constants.NOT_DELIVERED] and not status_transition[
            (delivery.status, data['status'])]:
            raise BadRequest(
                errorMessage='State transition not allowed from' + delivery.status + ' to ' + data['status'])
        delivery.status = data['status']
    delivery.save()
    order = delivery.order_set.last()

    # If last delivery delivered remove user membership
    if order.deliveries.last().status == delivery_constants.DELIVERED:
        user_handler.mark_unsubscribed_after_last_delivery(delivery.user)
        order.deliveries.all().update(deliveries_done=True)

    delivery.refresh_from_db()
    return delivery


def change_deliveries_status(args, data):
    if 'status' in data and 'ids' in args:
        ids = str(args['ids']).replace('/', '')
        deliveries, _ = get_deliveries_by_filter({'ids': ids})
        action_status = {}
        for delivery in deliveries:
            if data['status'] in [delivery_constants.DELIVERED, delivery_constants.NOT_DELIVERED] and not \
                    status_transition.get((delivery.status, data['status'],)):
                action_status[delivery.id] = {
                    'success': False,
                    'error': 'State transition not allowed from: ' + delivery.status + ' to: ' + data['status']}
            else:
                delivery.status = data['status']
                delivery.save()
                action_status[delivery.id] = {
                    'success': True,
                    'error': ''}
        return action_status


def get_delivery_harvest_data(deliveries):
    data = [delivery_constants.HARVEST_EXPORT_HEADERS]
    product_to_quantity_map = {}
    order_quantity = 0
    for delivery in deliveries:
        order_items = delivery.products.all()
        for item in order_items:
            order_quantity = ((float(item.quantity.quantity) / 1000) if item.quantity.unit in ['GM',
                                                                                               'ML'] else item.quantity.quantity) * item.order_quantity
            if item.product.name in product_to_quantity_map:
                product_to_quantity_map[item.product.name]['quantity'] += order_quantity
            else:
                product_to_quantity_map[item.product.name] = {'quantity': order_quantity,
                                                              'unit': 'PIECE' if item.quantity.unit == 'PIECE' else 'KG/LTR'}
    for name, value in product_to_quantity_map.items():
        data.append([name, value['quantity'], value['unit']])
    return data


def get_pdf_response_for_deliveries(deliveries):
    header = '<H1 align="center">Item details</H1>'
    table = '<table border="1" align="center" width="100%"><thead><tr><th width="75%">Item name</th> <th width="25%">Quantity </th></tr></thead><tbody>'
    end = '</tbody></table>'
    pdf = MyFPDF()
    for delivery in deliveries:
        user = delivery.user
        user_name = user.first_name + ' ' + user.last_name
        mobile_no = user.mobile
        delivery_date = delivery.delivery_date.strftime('%d/%m/%Y')
        lat, longt = delivery.address_for_delivery.latitude, delivery.address_for_delivery.longitude
        location_url = google_map_constant.MAP_PIN_URL + str(lat) + ',' + str(longt)
        user_details = '<p><strong>Customer Name  : </strong> ' + user_name + '<p><strong>Mobile No    :</strong> ' + mobile_no + '<p><strong>Address Location  :</strong> <a href=' + location_url + '>' + location_url + '</a><p><strong>Delivery date : <strong>' + delivery_date
        order_items = delivery.products.all()
        item_details = ''
        for item in order_items:
            item_details += '<tr> <td>' + item.product.name + '</td><td>' + str(
                item.quantity.quantity) + str(item.quantity.unit) + ' *' + str(item.order_quantity) + '</td></tr>'
        data = header + user_details + table + item_details + end
        pdf.add_page()
        pdf.write_html(data)
    response = make_response(pdf.output(name='members.pdf', dest='S'))
    response.headers.set('Content-Disposition', 'attachment', filename='members.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response


def update_delivery_address(user, address):
    user.delivery_set.filter(status=delivery_constants.SCHEDULED).update(
        address_for_delivery=address)
