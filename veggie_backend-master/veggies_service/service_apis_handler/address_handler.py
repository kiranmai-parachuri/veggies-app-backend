from veggies_service.constants import order_constants, delivery_constants
from veggies_service.db.veggies_models.models import Address
from veggies_service.service_apis_handler import pincode_handler
from veggies_service.utils.exceptions import BadRequest, NotFoundException, GenericCustomException
from veggies_service.views.address import AddressView


def create_address(data, user):
    address_data = {}
    try:
        address_data['location'] = data['location']
        address_data['address_line1'] = data['addressLine1']
        address_data['address_line2'] = data['addressLine2']
        address_data['pincode'] = pincode_handler.get_pincode_by_id(data['pincode'])
        address_data['latitude'] = data['latitude']
        address_data['longitude'] = data['longitude']
    except Exception as e:
        raise BadRequest(errorMessage="key error:" + str(e))
    if 'state' in data:
        address_data['state'] = data['state']
    if 'district' in data:
        address_data['district'] = data['district']
    if 'taluka' in data:
        address_data['taluka'] = data['taluka']
    if 'village' in data:
        address_data['village'] = data['village']
    address = Address.objects.create(**address_data)
    user.addresses.add(address)
    return address


def get_address_by_id(id):
    try:
        address = Address.objects.get(id=id)
        return address
    except Exception as e:
        raise NotFoundException(entity='Address')


def get_address_by_filter(user):
    return user.addresses.all()


def is_same_pincode(address, pincode):
    return address.pincode == pincode


def delete_address(id):
    address = get_address_by_id(id)
    if address.order_set.filter(status__in=[order_constants.CREATED]):
        raise GenericCustomException(message='Can not delete delivery address having created order')
    if address.delivery_address_here.filter(
            status__in=[delivery_constants.SCHEDULED, delivery_constants.EDITABLE, delivery_constants.FREEZE]):
        raise GenericCustomException(message='Can not delete delivery address having active deliveries')
    view = AddressView()
    res = view.render(address)
    address.delete()
    return {'address': res}


def update_address(id, data, user):
    address = get_address_by_id(id)
    if 'addressLine1' in data:
        address.address_line1 = data['addressLine1']
    if 'addressLine2' in data:
        address.address_line2 = data['addressLine2']
    if 'latitude' in data:
        address.latitude = data['latitude']
    if 'longitude' in data:
        address.longitude = data['longitude']
    if 'location' in data:
        address.location = data['location']
    address.save()
    address.refresh_from_db()
    return address
    # address = user.address
    # if not user.address:
    #     address = create_address(data, user)
    #     user.address = address
    #     user.save()
    #     return address
    # pincode = pincode_handler.get_pincode_by_id(data['pincode'])
    # if not is_same_pincode(address, pincode) and user_handler.does_user_have_membership(user):
    #     raise BadRequest(errorMessage='You can not change pincode while having active deliveries')
    # else:
    #     address_data = {'addressLine1': data['addressLine1'], 'addressLine2': data['addressLine2'],
    #                     'pincode': data['pincode']}
    #     address = create_address(address_data, user)
    #     delivery_handler.update_delivery_address(user, address)
    #     return address
