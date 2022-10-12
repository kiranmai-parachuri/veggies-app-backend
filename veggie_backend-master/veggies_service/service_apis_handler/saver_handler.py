from veggies_service.constants import savers_type, product_constant
from veggies_service.db.veggies_models.models import Saver
from veggies_service.service_apis_handler import product_handler
from veggies_service.utils.exceptions import NotFoundException, BadRequest, AlreadyExist
from veggies_service.views.saver import SaverView


def create_saver(data, user):
    saver_data = {'created_by': user}
    try:
        saver_data['saver_type'] = data['type']
        if not saver_data['saver_type'] in [savers_type.WEEK, savers_type.DAY]:
            raise BadRequest(errorMessage='saver type is could be WEEK or DAY')
        saver_data['product'] = product_handler.get_product_by_id(data['product'])
        if saver_data['product'].product_type != product_constant.NORMAL:
            raise BadRequest(errorMessage='Can only add Normal products to saver')
    except KeyError as e:
        raise BadRequest(errorMessage="key error:" + str(e))
    try:
        saver = Saver.objects.create(**saver_data)
    except Exception as e:
        raise AlreadyExist(entity='Saver')
    return saver


def get_savers():
    return Saver.objects.all()


def get_saver_by_id(id):
    try:
        return Saver.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Saver')


def delete_saver(id):
    saver = get_saver_by_id(id)
    view = SaverView()
    res = view.render(saver)
    saver.delete()
    return res
