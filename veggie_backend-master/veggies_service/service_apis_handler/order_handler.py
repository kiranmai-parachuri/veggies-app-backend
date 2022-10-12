from datetime import datetime, timedelta

from django.db import transaction

from veggies_service.constants import payment_constants, order_constants, delivery_constants, product_constant
from veggies_service.db.veggies_models.models import Order, Delivery, OrderItem, Address
from veggies_service.service_apis_handler import product_handler, basket_handler, slot_handler, \
    pincode_handler, coupon_handler
from veggies_service.services import razorpay_service
from veggies_service.utils.email_utils import send_order_delivered_email
from veggies_service.utils.exceptions import BadRequest, GenericCustomException, NotFoundException
from veggies_service.utils.fcm.FcmManager import order_delivered_notification


def check_product_availability(product, quantity, order_quantity):
    if quantity.unit in ['KG', 'LTR', 'GM', 'ML']:
        required_quantity = (quantity.quantity * 1000 if quantity.unit in ['KG',
                                                                           'LTR'] else quantity.quantity) * order_quantity
        # converting total_quantity to GM/ML
        if (product.total_quantity * 1000) - required_quantity > 0:
            return True
        else:
            return False
    elif quantity.unit in ['PIECE']:
        if product.total_quantity - (quantity.quantity * order_quantity) > 0:
            return True
        else:
            return False


def increase_product_quantity(items):
    for item in items:
        product = item.product
        quantity = item.quantity
        if quantity.unit == 'PIECE':
            required_quantity = quantity.unit * item.order_quantity
        else:
            required_quantity = (quantity.quantity if quantity.unit in ['KG',
                                                                        'LTR'] else float(
                quantity.quantity) / 1000) * item.order_quantity
        product.total_quantity += required_quantity
        if not product.in_stock and (product.total_quantity + required_quantity) >= 0:
            product.in_stock = True
        product.save()


def decrease_product_quantity(items):
    for item in items:
        product = item.product
        quantity = item.quantity
        if quantity.unit == 'PIECE':
            required_quantity = quantity.quantity * item.order_quantity
        else:
            required_quantity = (quantity.quantity if quantity.unit in ['KG',
                                                                        'LTR'] else float(
                quantity.quantity) / 1000) * item.order_quantity
        product.total_quantity -= required_quantity
        if (product.total_quantity - required_quantity) <= 0:
            product.in_stock = False
        product.save()


def create_order_payment_service(order_amount, user_id):
    order_response = razorpay_service.create_order(order_amount, user_id)
    return order_response


def update_order(id, request_data):
    orders, _ = get_orders_by_filter({'order_id': id})
    if not orders:
        raise NotFoundException(entity='Order')
    order = orders[0]
    if 'status' in request_data:
        if order.order_type == order_constants.ONE_TIME_BASKET:
            delivery = order.deliveries.last()
            delivery.status = request_data['status']
            delivery.save()
            if request_data['status'] == delivery_constants.DELIVERED:
                send_order_delivered_email(order)
                order_delivered_notification(order.created_by)
        order.delivery_status = request_data['status']
    if request_data['isSuccess']:
        payment_res = request_data['paymentSuccessResponse']
        order.payment_id = payment_res['paymentId']
        order.status = payment_constants.SUCCESS
    else:
        order.status = payment_constants.FAIL
    order.save()
    order.refresh_from_db()
    return order


def get_order_items_by_filter(data):
    criteria = {}
    if 'ids' in data:
        criteria['id__in'] = data['ids'].split(',')
    return OrderItem.objects.filter(**criteria)


def update_quantity_if_item_already_present(delivery, quantity, product, order_quantity):
    order_item = delivery.extra_products.filter(product=product, quantity=quantity).first()
    if order_item:
        order_item.order_quantity += order_quantity
    order_item.save()


def order_item_with_same_quantity_exists(delivery, product, quantity):
    return delivery.extra_products.filter(product=product, quantity=quantity).first()


def handle_order_items(order_items, is_basket=None, delivery=None):
    items = []

    for order in order_items:
        product = product_handler.get_product_by_id(order['productId'])
        if is_basket and not product.product_type == product_constant.BASKET:
            raise GenericCustomException(message='Product is not basket product: ' + str(product.name))
        if not is_basket and not product.product_type == product_constant.NORMAL:
            raise GenericCustomException(message='Product is not normal product: ' + str(product.name))
        quantity = product_handler.get_quantity_by_id(order['quantityId'])
        if not is_basket and check_product_availability(product, quantity, order['productQuantity']):
            if delivery and order_item_with_same_quantity_exists(delivery, product, quantity):
                update_quantity_if_item_already_present(delivery, quantity, product, order['productQuantity'])
            else:
                items.append(
                    OrderItem.objects.create(product=product, quantity=quantity,
                                             order_quantity=order['productQuantity']))
        elif is_basket:
            items.append(
                OrderItem.objects.create(product=product, quantity=quantity, order_quantity=order['productQuantity']))
        else:
            OrderItem.objects.filter(id__in=[x.id for x in items]).delete()
            raise GenericCustomException(message='Product out of stock: ' + product.name)
    return items


def check_order_amount(amount, order_items):
    total_amount = 0
    for order in order_items:
        quantity = product_handler.get_quantity_by_id(order['quantityId'])
        total_amount += (quantity.price * quantity.quantity)
    return amount == total_amount


def get_delivery_dates_for_slot(slot, deliveries):
    delivery_dates = []
    todays_date = datetime.now()
    slot_day = slot.day
    delta = slot_day - todays_date.weekday()
    if delta > 0:
        if (delta - delivery_constants.DELIVERY_PRIOR_DAYS) >= 0:
            next_week_day = delta
        else:
            next_week_day = abs(delta) + delivery_constants.TOTAL_WEEK_DAYS
    else:
        diff = delta + delivery_constants.TOTAL_WEEK_DAYS
        if (diff - delivery_constants.DELIVERY_PRIOR_DAYS) >= 0:
            next_week_day = diff
        else:
            next_week_day = diff + delivery_constants.TOTAL_WEEK_DAYS

    next_delivery_date = (todays_date + timedelta(days=next_week_day)).replace(hour=slot.start_time.hour, minute=0,
                                                                               second=0)
    return get_deliveries_for_start_date(deliveries, delivery_dates, next_delivery_date, slot)


def get_deliveries_for_start_date(deliveries, delivery_dates, next_delivery_date, slot):
    delivery_dates.append(next_delivery_date)
    for i in range(deliveries - 1):
        next_delivery_date += timedelta(days=delivery_constants.TOTAL_WEEK_DAYS)
        delivery_dates.append(next_delivery_date.replace(hour=slot.start_time.hour, minute=0, second=0))
    return delivery_dates


def create_deliveries(basket, user, slot, address):
    deliveries = []
    max_points = basket.points / basket.deliveries
    delivery_dates = get_delivery_dates_for_slot(slot, basket.deliveries)
    for i in range(basket.deliveries):
        deliveries.append(Delivery.objects.create(user=user, basket=basket,
                                                  delivery_no=i + 1, slot=slot,
                                                  max_points=max_points, delivery_date=delivery_dates[i],
                                                  address_for_delivery=address))
    return deliveries


def get_next_delivery_for_user(user):
    order_with_basket = Order.objects.filter(created_by=user, order_type=order_constants.BASKET).last()
    return order_with_basket.deliveries.filter(status__in=[delivery_constants.SCHEDULED,
                                                           delivery_constants.FREEZE,
                                                           delivery_constants.EDITABLE]).first()


def add_order_items_to_delivery_basket(items, user):
    next_to_previous_delivery = get_next_delivery_for_user(user)
    next_to_previous_delivery.extra_products.add(*items)


@transaction.atomic
def handle_order_fail(order):
    user = order.created_by
    if order.order_type == order_constants.BASKET:
        user.does_hold_membership = False
        user.save()
    elif order.order_type == order_constants.NORMAL:
        order_items = order.items.all()
        delivery = get_next_delivery_for_user(user)
        if delivery:
            delivery.extra_products.remove(*order_items)
        increase_product_quantity(order_items)
        order_items.delete()
        order.save()
    elif order.order_type == order_constants.ONE_TIME_BASKET:
        order_items = order.items.all()
        order_items.delete()


def is_coupon_avail_by_user(coupon, user):
    try:
        coupon = coupon_handler.get_coupon_avail_for_user_and_coupon(coupon, user)
        if coupon:
            return True
    except NotFoundException as e:
        return False


@transaction.atomic
def create_order(request_data, user):
    order_data = {'created_by': user}
    if not user.is_email_verified:
        raise GenericCustomException(message='User must be verified')
    try:
        order_data['total_amount'] = request_data['amount']
    except Exception as e:
        raise BadRequest(errorMessage="key error:" + str(e))
    items = None
    order_response = create_order_payment_service(order_data['total_amount'], user.mobile)
    if 'orderItems' in request_data:
        if request_data['withBasket'] and not 'address' in request_data:
            order_with_basket = Order.objects.filter(created_by=user, order_type=order_constants.BASKET).last()
            if not order_with_basket:
                raise BadRequest(errorMessage='User dont have basket')
            basket = order_with_basket.basket
            order_data['basket'] = basket
            order_data['with_basket_delivery'] = True
            order_items = request_data['orderItems']
            next_delivery = get_next_delivery_for_user(user)
            if 'extendedDeliveryId' in request_data:
                items = handle_order_items(order_items, delivery=next_delivery, is_basket=True)
                order_data['extended_delivery'] = next_delivery

            else:
                items = handle_order_items(order_items, delivery=next_delivery)
                next_delivery.extra_products.add(*items)
        else:
            address = ___get_or_create_address(request_data, user)
            if not user.addresses.filter(id=address.id):
                raise BadRequest(errorMessage='Address is not mapped with user')
            order_data['address'] = address
            order_items = request_data['orderItems']
            items = handle_order_items(order_items)
    order = Order.objects.create(**order_data)
    if items:
        order.items.add(*items)
    if items and not 'extendedDeliveryId' in request_data:
        decrease_product_quantity(items)
    order.order_response = order_response
    order.order_id = order_response['id']
    if 'coupon' in request_data:
        check_and_apply_coupon(order, request_data, user)
    if 'orderType' in request_data:
        address = ___get_or_create_address(request_data, user)
        if not user.addresses.filter(id=address.id):
            raise BadRequest(errorMessage='Address is not mapped with user')
        try:
            basket = basket_handler.get_basket_by_id(request_data['basket'])
            order.order_type = order_constants.BASKET
            order.basket = basket
        except Exception as e:
            raise BadRequest(errorMessage="key error:" + str(e))

        # create basket type order
        if not basket.is_one_time_delivery:
            try:
                slot = slot_handler.get_slot_by_id(request_data['slot'])
            except Exception as e:
                raise BadRequest(errorMessage="key error:" + str(e))
            order.slot = slot
        # create one time basket type order
        elif basket.is_one_time_delivery:
            items = create_order_items_for_basket_products(basket)
            order.items.add(*items)
            order.order_type = order_constants.ONE_TIME_BASKET
        order.address = address
    order.save()
    order.refresh_from_db()
    return order


def create_deliveries_for_basket_order(order):
    user = order.created_by
    slot = order.slot
    address = order.address
    basket = order.basket
    deliveries = create_deliveries(basket, user, slot, address)
    # Set membership to user
    user.does_hold_membership = True
    user.save()
    order.deliveries.add(*deliveries)


def create_order_items_for_basket_products(basket):
    items = []
    for product in basket.products.all():
        items.append(OrderItem.objects.create(product=product, quantity=product.plan_details, order_quantity=1))
    return items


@transaction.atomic
def check_and_apply_coupon(order, request_data, user):
    # apply coupon
    coupon = coupon_handler.get_coupons_by_filter({'coupon_code': request_data['coupon']}).first()
    if coupon:
        can_apply, message = coupon_handler.is_coupon_usable(coupon, user)
    else:
        raise NotFoundException('Coupon')
    if not can_apply:
        raise BadRequest(errorMessage=message)
    order.coupon = coupon
    coupon.remaining_count -= 1
    coupon.save()
    coupon_handler.create_coupon_avail(coupon, user)


def ___get_or_create_address(data, user):
    try:
        address = data['address']
    except Exception as e:
        raise BadRequest(errorMessage="key error:" + str(e))
    if not address['isNew']:
        address = Address.objects.get(id=address['id'])
    else:
        address_data = {}
        try:
            address_data['location'] = address['location']
            address_data['address_line1'] = address['addressLine1']
            address_data['address_line2'] = address['addressLine2']
            address_data['pincode'] = pincode_handler.get_pincode_by_id(address['pincode'])
            address_data['latitude'] = address['latitude']
            address_data['longitude'] = address['longitude']
        except Exception as e:
            raise BadRequest(errorMessage="key error:" + str(e))
        if 'state' in data:
            address_data['state'] = address['state']
        if 'district' in data:
            address_data['district'] = address['district']
        if 'taluka' in data:
            address_data['taluka'] = address['taluka']
        if 'village' in data:
            address_data['village'] = address['village']
        address = Address.objects.create(**address_data)
        user.addresses.add(address)
    return address


def get_order_by_id(id):
    try:
        return Order.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Order')


def clear_created_orders(user):
    orders = Order.objects.filter(created_by=user, status=payment_constants.CREATED)
    OrderItem.objects.filter(id__in=[x.id for x in orders]).delete()
    for o in orders:
        o.delete()


def get_orders_by_filter(data, user=None):
    # clear_created_orders(user)
    criteria = {}
    start_index = end_index = None
    if 'page' in data and 'perPage' in data:
        page = int(data['page'])
        per_page = int(data['perPage'])
        end_index = page * per_page
        start_index = end_index - per_page
    if user:
        criteria['created_by'] = user
        if 'status' in data:
            criteria['status__in'] = data['status'].split(',')
        if end_index:
            orders = Order.objects.filter(**criteria).order_by('-id')
            return orders[start_index:end_index], len(orders)
        orders = Order.objects.filter(**criteria).order_by('-id')
        return orders, len(orders)
    if 'user' in data:
        criteria['created_by__mobile__in'] = data['user'].split(',')
    if 'status' in data:
        criteria['status__in'] = data['status'].split(',')
    if 'orderId' in data:
        criteria['order_id'] = data['orderId']
    if 'type' in data:
        criteria['order_type'] = data['type']
    if end_index:
        orders = Order.objects.filter(**criteria).order_by('-id')
        return orders[start_index:end_index], len(orders)
    orders = Order.objects.filter(**criteria).order_by('-id')
    return orders, len(orders)
# if __name__ == '__main__':
#     import django;
#
#     django.setup()
#     from veggies_service.db.veggies_models.models import Slot, User
#
#     s, t = Slot.objects.get_or_create(day=2, created_by=User.objects.first())
#     print get_delivery_dates_for_slot(s, 4)
