from django.db import transaction

from veggies_service.constants import delivery_constants, order_constants
from veggies_service.db.veggies_models.models import Basket
from veggies_service.service_apis_handler import product_handler
from veggies_service.utils import string_utils
from veggies_service.utils.exceptions import BadRequest, NotFoundException
from veggies_service.utils.file_utils import delete_file, update_file_from_request, \
    save_file_from_request
from veggies_service.views.basket import BasketView

@transaction.atomic
def create_basket(request, user):
    data = request.form.to_dict()
    basket_details = {'created_by': user}
    try:
        basket_details['name'] = data['name']
        basket_details['points'] = data['points']
        basket_details['deliveries'] = data['deliveries']
        basket_details['price'] = data['price']
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    basket_details['image'] = save_file_from_request(request)
    if 'description' in data:
        basket_details['description'] = string_utils.string_marshal(data['description'])
    products = None
    if 'products' in data:
        products, _ = product_handler.get_products_by_filter({'id': data['products']})
    if int(data['deliveries']) == 0:
        basket_details['is_one_time_delivery'] = True
    basket = Basket.objects.create(**basket_details)
    if products:
        basket.products.add(*products)
    return basket


def get_basket_by_id(id):
    try:
        basket_object = Basket.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Basket')
    return basket_object


def get_basket_by_filter(data):
    criteria = {'show': True}
    if 'id' in data:
        criteria['id__in'] = data['id'].split(',')
    if 'user' in data:
        criteria['created_by_id'] = data['user']
    start_index = end_index = None
    if 'page' in data and 'perPage' in data:
        page = int(data['page'])
        per_page = int(data['perPage'])
        end_index = page * per_page
        start_index = end_index - per_page
    if end_index:
        baskets = Basket.objects.filter(**criteria)
        return baskets[start_index:end_index], len(baskets)
    baskets = Basket.objects.filter(**criteria)
    return baskets, len(baskets)


def update_basket(id, request):
    data = request.form.to_dict()
    basket = get_basket_by_id(id)
    if 'name' in data:
        basket.name = data['name']
    if 'points' in data:
        basket.points = data['points']
    if 'deliveries' in data:
        if data['deliveries'] == 0:
            basket.is_one_time_delivery = True
            basket.deliveries = 1
        else:
            basket.is_one_time_delivery = False
            basket.deliveries = data['deliveries']
    if 'price' in data:
        basket.price = data['price']
    if 'unit' in data:
        basket.unit = data['unit']
    if 'show' in data:
        basket.show = eval(data['show'])
    if request.files or 'file' in data:
        basket.image = update_file_from_request(request, basket)

    if request.files or 'file' in data:
        basket.image = update_file_from_request(request, basket)
    products = None
    if 'products' in data:
        products, _ = product_handler.get_products_by_filter({'id': data['products']})
    if products:
        basket.products.add(*products)
    basket.save()
    basket.refresh_from_db()
    return basket


def delete_basket(id):
    basket = get_basket_by_id(id)
    if basket.order_set.filter().exclude(status=order_constants.FAIL):
        raise BadRequest(errorMessage='Basket have orders with it')
    if basket.delivery_set.filter().exclude(
            status__in=[delivery_constants.DELIVERED, delivery_constants.NOT_DELIVERED]):
        raise BadRequest(errorMessage='Basket has active deliveries')
    view = BasketView()
    res = view.render(basket)
    delete_file(basket.image)
    basket.delete()
    return {'basket': res}
