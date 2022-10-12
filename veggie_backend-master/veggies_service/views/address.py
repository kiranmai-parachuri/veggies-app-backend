from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender
from veggies_service.views.pincode import PincodeView


class AddressView(SchemaRender):
    id = fields.Integer()
    state = fields.String()
    district = fields.String()
    taluka = fields.String()
    village = fields.String()
    pincode = fields.Nested(PincodeView)
    address_line1 = fields.String(dump_to="addressLine1")
    address_line2 = fields.String(dump_to="addressLine2")
    longitude = fields.Float(dump_to='longitude')
    latitude = fields.Float(dump_to='latitude')
    location = fields.String()
