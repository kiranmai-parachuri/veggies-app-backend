from veggies_service.db.veggies_models.models import Pincode
from veggies_service.service_apis_handler import slot_handler
from veggies_service.utils.exceptions import BadRequest, NotFoundException
from veggies_service.views.pincode import PincodeView


def get_pincodes():
    return Pincode.objects.all()


def create_pincode(data, user):
    pincode_data = {'created_by': user}
    try:
        pincode_data['pincode'] = data['pincode']
        pincode_data['delivery_charges'] = data['deliveryCharges']
        slots = data['slots']
        pincode_data['delivery_days'] = data['deliveryDays']
    except KeyError as e:
        raise BadRequest(errorMessage="key error:" + str(e))
    pincode = Pincode.objects.create(**pincode_data)
    slots, _ = slot_handler.get_slots_by_filter({'ids': slots})
    if not slots:
        raise NotFoundException(entity='Slot')
    pincode.slot.add(*slots)
    pincode.refresh_from_db()
    return pincode


def get_pincode_by_id(id):
    try:
        return Pincode.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Pincode')


def update_pincode(id, data):
    pincode = get_pincode_by_id(id)
    if 'pincode' in data:
        pincode.pincode = data['pincode']
    if 'deliveryCharges' in data:
        pincode.delivery_charges = data['deliveryCharges']
    if 'slots' in data:
        slots, _ = slot_handler.get_slots_by_filter({'ids': data['slots']})
        pincode.slot.clear()
        pincode.slot.add(*slots)
    pincode.save()
    pincode.refresh_from_db()
    return pincode


def delete_pincode(id):
    pincode = get_pincode_by_id(id)
    view = PincodeView()
    res = view.render(pincode)
    pincode.delete()
    return res
