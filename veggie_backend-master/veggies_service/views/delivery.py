from marshmallow import fields

from veggies_service.constants import google_map_constant
from veggies_service.utils import datetime_utils
from veggies_service.views.address import AddressView
from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.order_item import OrderItemView
from veggies_service.views.slot import SlotView
from veggies_service.views.user import UserBasicView


class DeliveryView(SchemaRender):
    id = fields.Integer()
    user = fields.Nested(UserBasicView)
    products = fields.Method('get_products')
    delivery_date = DateTimeEpoch(dump_to='deliveryDate')
    delivery_no = fields.Integer(dump_to='deliveryNo')
    slot = fields.Nested(SlotView)
    max_points = fields.Integer(dump_to='maxPoints')
    used_points = fields.Integer(dump_to='usedPoints')
    extra_products = fields.Method('get_extra_products', dump_to='extraProducts')
    status = fields.String()
    is_default_delivery = fields.Boolean(dump_to='isDefaultDelivery')
    customizationStartDate = fields.Method('get_customization_start')
    customizationEndDate = fields.Method('get_customization_end')
    basketName = fields.Method('get_basket_name')
    address_for_delivery = fields.Nested(AddressView, dump_to='deliveryAddress')
    deliveryLocation = fields.Method('get_delivery_location')
    isExtendedDelivery = fields.Method('is_extended_delivery')
    isOneTimeDelivery = fields.Method('is_one_time_delivery')

    def is_one_time_delivery(self, obj):
        return obj.basket.is_one_time_delivery

    def is_extended_delivery(self, obj):
        if obj.products.all():
            used_points = sum([oi.quantity.price * oi.order_quantity for oi in obj.products.all()])
            return used_points > obj.max_points
        else:
            return False

    def get_delivery_location(self, obj):
        lat, longt = obj.address_for_delivery.latitude, obj.address_for_delivery.longitude
        return google_map_constant.MAP_PIN_URL + str(lat) + ',' + str(longt)

    def get_basket_name(self, obj):
        return obj.basket.name

    def get_customization_start(self, obj):
        date = datetime_utils.get_customization_start_date(obj)
        return int(date.strftime('%s')) * 1000

    def get_customization_end(self, obj):
        date = datetime_utils.get_customization_end_date(obj)
        return int(date.strftime('%s')) * 1000

    def get_products(self, obj):
        products = obj.products.all()
        v = OrderItemView()
        return [v.render(product) for product in products]

    def get_extra_products(self, obj):
        extra_products = obj.extra_products.all()
        v = OrderItemView()
        return [v.render(product) for product in extra_products]
