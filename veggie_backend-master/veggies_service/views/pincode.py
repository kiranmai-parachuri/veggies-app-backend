from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender
from veggies_service.views.slot import SlotView


class PincodeView(SchemaRender):
    id = fields.Integer()
    pincode = fields.Integer()
    delivery_charges = fields.Float(dump_to='deliveryCharges')
    slot = fields.Method('get_slots')
    delivery_days = fields.Integer(dump_to='deliveryDays')

    def get_slots(self, obj):
        slots = obj.slot.all()
        v = SlotView()
        return [v.render(slot) for slot in slots]
