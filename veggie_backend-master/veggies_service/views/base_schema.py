from marshmallow import Schema, fields


class DateTimeEpoch(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return 0
        return int(value.strftime('%s')) * 1000


class SchemaRender(Schema):
    def render(self, object):
        return self.dump(object).data
