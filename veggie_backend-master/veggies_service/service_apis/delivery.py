import StringIO
from datetime import datetime
import mimetypes

import xlsxwriter
from flask import Response
from flask import request
from werkzeug.datastructures import Headers

from veggies_service.constants import delivery_constants, user_role, order_constants
from veggies_service.service_apis_handler import delivery_handler, user_handler
from veggies_service.utils.exceptions import UnauthorisedException
from veggies_service.utils.pdf_utils import get_pdf
from veggies_service.utils.resource import BaseResource
from veggies_service.utils.user_context import is_logged_in_user_customer, get_user_object, is_logged_in_user_admin, \
    get_user_role
from veggies_service.views.basket import BasketView
from veggies_service.views.delivery import DeliveryView
from veggies_service.views.slot import SlotView


def get_slot_wise_response(deliveries):
    slot_to_delivery_map = {}
    for delivery in deliveries:
        if delivery.slot in slot_to_delivery_map:
            slot_to_delivery_map[delivery.slot].append(delivery)
        else:
            slot_to_delivery_map[delivery.slot] = [delivery]
    delivery_view = DeliveryView()
    slot_view = SlotView()
    slots = []
    for slot, deliveries in slot_to_delivery_map.items():
        slot_response = slot_view.render(slot)
        slot_response['deliveries'] = [delivery_view.render(delivery) for delivery in slot_to_delivery_map[slot]]
        slots.append(slot_response)
    return {'slots': slots}


def get_harvesting_details_as_excel(data):
    try:
        response = Response()
        response.status_code = 200
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('sarpanch')
        for i, d in enumerate(data):
            for j, res in enumerate(d):
                worksheet.write(i, j, res)
        workbook.close()
        output.seek(0)
        response.data = output.read()
        file_name = 'harvesring_details_{}.xlsx'.format(
            datetime.now().strftime('%d/%m/%Y'))
        mimetype_tuple = mimetypes.guess_type(file_name)
        response_headers = Headers({
            'Pragma': "public",  # required,
            'Expires': '0',
            'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
            'Cache-Control': 'private',  # required for certain browsers,
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename=\"%s\";' % file_name,
            'Content-Transfer-Encoding': 'binary',
            'Content-Length': len(response.data)
        })

        if not mimetype_tuple[1] is None:
            response.update({
                'Content-Encoding': mimetype_tuple[1]
            })
        response.headers = response_headers
        response.set_cookie('fileDownload', 'true', path='/')
        return response
    except Exception as e:
        print e


class Delivery(BaseResource):
    def get(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        data = request.args
        user = get_user_object(token)
        # user = user_handler.get_user_by_mobile('9637552245')
        view = DeliveryView()
        b_view = BasketView()
        if is_logged_in_user_customer(token):
            deliveries, count = delivery_handler.get_deliveries_by_filter({'user': user.mobile, 'deliveries_done': False})
        else:
            if 'harvestDetails' in data:
                if 'ids' in data:
                    ids = str(data['ids']).replace('/', '')
                    data.update({'ids': ids})
                deliveries, _ = delivery_handler.get_deliveries_by_filter(data)
                data = delivery_handler.get_delivery_harvest_data(deliveries)
                return get_harvesting_details_as_excel(data)
            elif 'pdfExport' in data:
                if 'ids' in data:
                    ids = str(data['ids']).replace('/', '')
                    data.update({'ids': ids})
                deliveries, _ = delivery_handler.get_deliveries_by_filter(data)
                return delivery_handler.get_pdf_response_for_deliveries(deliveries)
            deliveries, count = delivery_handler.get_deliveries_by_filter(data)
        delivery_handler.mark_delivery_editable_if_customization_start(deliveries)

        delivery_handler.mark_delivery_freeze_if_customization_end(deliveries)
        if is_logged_in_user_customer(token) and data.get('productsEstimate'):
            return delivery_handler.get_products_estimate_for_delivery(id)
        if is_logged_in_user_admin(token) and data.get('slotWise'):
            deliveries, _ = delivery_handler.get_deliveries_by_filter({'status': delivery_constants.FREEZE})
            return get_slot_wise_response(deliveries)
        if is_logged_in_user_admin(token):
            return {'deliveries': [view.render(delivery) for delivery in deliveries],
                    'total': count}
        return {'deliveries': [view.render(delivery) for delivery in deliveries],
                    'total': count,
                    'basket': b_view.render(user.order_set.filter(order_type=order_constants.BASKET).last().basket) if user.order_set.filter(order_type=order_constants.BASKET) else {}}

    def put(self, id=None):
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if get_user_role(token) not in [user_role.ADMIN, user_role.CUSTOMER]:
            raise UnauthorisedException()
        user = get_user_object(token)
        data = request.get_json(force=True)
        args = request.args
        if get_user_role(token) == user_role.ADMIN:
            if 'status' in data and 'ids' in args:
                return {'actionStatus': delivery_handler.change_deliveries_status(args, data)}
        delivery = delivery_handler.update_delivery(id, data, user)
        view = DeliveryView()
        return {'delivery': view.render(delivery)}
