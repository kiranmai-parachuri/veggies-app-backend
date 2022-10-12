from marshmallow import fields

from veggies_service.views.base_schema import SchemaRender


class UserBasicView(SchemaRender):
    id = fields.String()
    mobile = fields.String(dump_to='mobile')
    first_name = fields.String(dump_to='firstName')
    last_name = fields.String(dump_to='lastName')
    does_hold_membership = fields.Boolean(dump_to='doesHoldMembership')
    email = fields.String()
    role = fields.String()
    is_email_verified = fields.Boolean(dump_to='isEmailVerified')
    fcm_id = fields.String(dump_to='fcmId')
