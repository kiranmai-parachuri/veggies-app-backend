from marshmallow import fields

from marshmallow import fields

from veggies_service.constants import google_map_constant
from veggies_service.utils.order import get_delivery_date_for_order
from veggies_service.views.address import AddressView
from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.coupon import CouponView
from veggies_service.views.delivery import DeliveryView
from veggies_service.views.order_item import OrderItemView
from veggies_service.views.user import UserBasicView


class OrderView(SchemaRender):
    id = fields.Integer()
    created_by = fields.Nested(UserBasicView)
    items = fields.Method('get_items')
    total_amount = fields.Float(dump_to='totalAmount')
    order_id = fields.String(dump_to='orderId')
    payment_id = fields.String(dump_to='paymentId')
    status = fields.String()
    order_type = fields.String(dump_to='orderType')
    deliveries = fields.Method('get_deliveries')
    created_on = DateTimeEpoch(dump_to='createdOn')
    does_have_query = fields.Boolean(dump_to='doesHaveQuery')
    deliveryDate = fields.Method('get_delivery_date')
    address = fields.Nested(AddressView)
    coupon = fields.Nested(CouponView)
    with_basket_delivery = fields.Boolean(dump_to='withBasketDelivery')
    delivery_status = fields.String(dump_to='deliveryStatus')
    deliveryLocation = fields.Method('get_delivery_location')
    extended_delivery = fields.Method('get_extended_delivery_id', dump_to='extendedDelivery')

    def get_extended_delivery_id(self, obj):
        return obj.extended_delivery.id if obj.extended_delivery else ''

    def get_delivery_location(self, obj):
        lat, longt = obj.address.latitude, obj.address.longitude
        return google_map_constant.MAP_PIN_URL + str(lat) + ',' + str(longt)

    def get_items(self, obj):
        view = OrderItemView()
        return [view.render(x) for x in obj.items.all()]

    def get_deliveries(self, obj):
        deliveries = obj.deliveries.all()
        v = DeliveryView()
        return [v.render(delivery) for delivery in deliveries]

    def get_delivery_date(self, obj):
        delivery_date = get_delivery_date_for_order(obj)
        return int(delivery_date.strftime('%s')) * 1000
