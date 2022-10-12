from flask import request, app

from veggies_service.service_apis_handler.version_handler import get_latest_version_for_device, \
    create_version_object_post, update_version_object
from veggies_service.utils.resource import BaseResource
from veggies_service.views import version


class Version(BaseResource):
    def get(self):
        request_data = request.args
        # app.logger.info("Version GET  request {}".format(request_data))
        latest_version = get_latest_version_for_device(request_data)
        return latest_version
    get.authenticated = False

    def post(self):
        request_data = request.get_json(force=True)
        # app.logger.info("Vesrion POST request {}".format(request_data))
        version_object = create_version_object_post(request_data)
        view = version.VersionView()
        return {"version": view.render(version_object)}

    def put(self, version_id):
        request_data = request.get_json(force=True)
        # app.logger.info("Vesrion PUT request {}".format(request_data))
        version_object = update_version_object(request_data, version_id)
        view = version.VersionView()
        return {"version": view.render(version_object)}
