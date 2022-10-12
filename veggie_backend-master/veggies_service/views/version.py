import json
from marshmallow import fields

from veggies_service.views import version_features
from veggies_service.views.base_schema import SchemaRender


class VersionView(SchemaRender):
    id = fields.String()
    version_name = fields.String(dump_to="versionName")
    update_type = fields.String(dump_to="updateType")
    product = fields.String()
    features = fields.Method('get_features')

    def get_features(self, obj):
        features = obj.versionfeature_set.all()
        view = version_features.Complete()
        return [view.render(feature) for feature in features]

