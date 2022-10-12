from marshmallow import fields

from veggies_service.views.base_schema import DateTimeEpoch, SchemaRender
from veggies_service.views.user import UserBasicView


class CouponView(SchemaRender):
    id = fields.Integer()
    coupon_code = fields.String(dump_to='couponCode')
    apply_count = fields.Integer(dump_to='applyCount')
    remaining_count = fields.Integer(dump_to='remainingCount')
    user = fields.Nested(UserBasicView)
    created_on = DateTimeEpoch(dump_to='createdOn')
    start_time = DateTimeEpoch('startTime')
    end_time = DateTimeEpoch('endTime')
    is_deleted = fields.Boolean()
    price = fields.Float()