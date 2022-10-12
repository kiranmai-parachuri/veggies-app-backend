import json

from django.db import transaction

from veggies_service.constants import product_constant, user_role
from veggies_service.db.veggies_models.models import Product, Quantities
from veggies_service.service_apis_handler import category_handler
from veggies_service.utils import string_utils
from veggies_service.utils.exceptions import BadRequest, NotFoundException, GenericCustomException
from veggies_service.utils.file_utils import delete_file, save_file_from_request, \
    update_file_from_request
from veggies_service.views.product import ProductView


def create_normal_product(data):
    product_details = {'created_by': data['user']}
    try:
        product_details['name'] = data['name']
        category_name = data['category']
        product_details['category'] = category_handler.get_category_by_id(category_name)
        product_details['total_quantity'] = data['totalQuantity']
        product_quantities = json.loads(data['quantities'])
        product_details['mrp'] = data['mrp']
        product_details['price'] = data['price']
        product_details['unit'] = data['unit']
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    if not product_quantities:
        raise BadRequest(errorMessage='There must be one quantity for product')
    product_details['product_type'] = product_constant.NORMAL

    if 'healthBenefits' in data:
        product_details['health_benefits'] = string_utils.string_marshal(data['healthBenefits'])
    if 'nutritionBenefits' in data:
        product_details['nutrition_benefits'] = string_utils.string_marshal(data['nutritionBenefits'])
    if 'description' in data:
        product_details['description'] = data['description']
    product_details['image'] = data['image']
    quantities = []
    if 'quantities' in data:
        for q in product_quantities:
            quantities.append(Quantities.objects.create(price=q['price'], unit=q['unit'], quantity=q['quantity']))
    try:
        product = Product.objects.create(**product_details)
    except Exception as e:
        raise GenericCustomException(message='Error while creating product. Error: ' + str(e))
    if quantities:
        product.quantities.add(*quantities)
    return product


def create_basket_product(data):
    product_details = {'created_by': data['user']}
    try:
        product_details['name'] = data['name']
        product_details['product_type'] = product_constant.BASKET
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    try:
        plan_details = json.loads(data['planDetails'])
        product_details['plan_details'] = Quantities.objects.create(price=plan_details['points'],
                                                                    unit=plan_details['unit'],
                                                                    quantity=plan_details['quantity'])
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    product_details['image'] = data['image']
    try:
        product = Product.objects.create(**product_details)
    except Exception as e:
        raise GenericCustomException(message='Error while creating product. Error: ' + str(e))
    return product


@transaction.atomic
def create_product(request, user):
    data = request.form.to_dict()
    product_type = data['type']
    filename = save_file_from_request(request)
    data['image'] = filename
    data['user'] = user
    if product_type.upper() == product_constant.NORMAL:
        product = create_normal_product(data)
    else:
        product = create_basket_product(data)
    return product


def update_product(request, name):
    product_object = get_product_by_id(name)
    data = request.form.to_dict()
    if 'name' in data:
        product_object.name = data['name']
    if 'show' in data:
        product_object.show = eval(data['show'])
    if request.files or 'file' in data:
        product_object.image = update_file_from_request(request, product_object)
    if product_object.product_type == product_constant.NORMAL:
        if 'category' in data:
            category_id = data['category']
            product_object.category = category_handler.get_category_by_id(category_id)
        if 'totalQuantity' in data:
            product_object.total_quantity = float(data['totalQuantity'])
            if not product_object.in_stock and float(data['totalQuantity']) > 0:
                product_object.in_stock = True
            if product_object.in_stock and float(data['totalQuantity']) <= 0:
                product_object.in_stock = False
        if 'mrp' in data:
            product_object.mrp = data['mrp']
        if 'price' in data:
            product_object.price = data['price']
        if 'unit' in data:
            product_object.unit = data['unit']
        if 'healthBenefits' in data:
            product_object.health_benefits = string_utils.string_marshal(data['healthBenefits'])
        if 'nutritionBenefits' in data:
            product_object.nutrition_benefits = string_utils.string_marshal(data['nutritionBenefits'])
        if 'description' in data:
            product_object.description = data['description']
        quantities = []
        if 'quantities' in data:
            product_quantities = json.loads(data['quantities'])
            for q in product_quantities:
                quantities.append(Quantities.objects.create(price=q['price'], unit=q['unit'], quantity=q['quantity']))
        if quantities:
            product_object.quantities.clear()
            product_object.quantities.add(*quantities)
    if product_object.product_type == product_constant.BASKET:
        if 'planDetails' in data:
            plan_details = json.loads(data['planDetails'])
            product_object.plan_details = Quantities.objects.create(price=plan_details['points'],
                                                                    unit=plan_details['unit'],
                                                                    quantity=plan_details['quantity'])
    product_object.save()
    product_object.refresh_from_db()
    return product_object


def get_product_by_id(id):
    try:
        product_object = Product.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Product')
    return product_object


def get_quantity_by_id(id):
    try:
        quantity_object = Quantities.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Quantity')
    return quantity_object


def delete_product(name):
    product = get_product_by_id(name)
    baskets = product.basket_set.all()
    if baskets:
        raise BadRequest('can not delete product which is mapped to baskets :' + ','.join([b.name for b in baskets]))

    savers = product.saver_set.all()
    if savers:
        raise BadRequest('can not delete product which is mapped to savers')
    view = ProductView()
    res = view.render(product)
    delete_file(product.image)
    product.delete()
    return res


def get_products_by_filter(data, user=None):
    filter_criteria = {'show': True}
    if user:
        if user.role == user_role.ADMIN:
            filter_criteria.pop('show')
            filter_criteria['show__in'] = [True, False]
    if 'id' in data:
        filter_criteria['id__in'] = data['id'].split(',')
    if 'category' in data:
        filter_criteria['category__id__in'] = data['category'].split(',')
    if 'type' in data:
        filter_criteria['product_type'] = data['type'].upper()
    start_index = end_index = None
    if 'page' in data and 'perPage' in data:
        page = int(data['page'])
        per_page = int(data['perPage'])
        end_index = page * per_page
        start_index = end_index - per_page
    if end_index:
        products = Product.objects.filter(**filter_criteria)
        return products[start_index:end_index], len(products)
    products = Product.objects.filter(**filter_criteria)
    return products, len(products)
