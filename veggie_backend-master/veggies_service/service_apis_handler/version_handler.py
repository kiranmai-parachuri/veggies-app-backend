from veggies_service.constants import update_type_constants
from veggies_service.daos.version_db_calls import get_version_objects_after, create_version_object, \
    create_feature_objects, get_version_object_by_id


def get_latest_version_for_device(request_data, product_name='APP'):
    current_version = request_data['versionName']
    version_objects = get_version_objects_after(current_version, product_name)
    is_latest = True
    if len(version_objects) == 0:
        is_latest = False
        return latest_version_response(None, is_latest)
    else:
        is_mandatory = is_mandatory_version_there(version_objects)
        features = get_all_features(version_objects)
        return latest_version_response(version_objects[0], is_latest,
                                       is_mandatory,
                                       features)


def is_mandatory_version_there(version_objects):
    for version_object in version_objects:
        if version_object.update_type == update_type_constants.UPDATE_MANDATORY:
            return True
    return False


def get_all_features(version_objects):
    features = []
    index = 1
    for version_feature in version_objects:
        version_features = []
        for feature in version_feature.versionfeature_set.all():
            version_features.append(str(index) + ". " + feature.feature)
            index += 1
        features.extend(version_features)
    return features


def latest_version_response(version_object, is_latest, is_mendatory=None,
                            features=None):
    if not is_latest:
        return {"isLatest": True}

    else:
        update_details = {
            "id": version_object.id,
            "latestVersionName": version_object.version_name,
            "updateFeatures": features}
        return {"isLatest": False,
                "updateType": update_type_constants.UPDATE_MANDATORY if is_mendatory else update_type_constants.UPDATE_TRIVIAL,
                "updateDetails": update_details}


def create_version_object_post(request_data):
    version = request_data['version']
    version_dictionary = {"version_name": version['versionName'],
                          "update_type": version['updateType'],
                          "product": "APP"}
    version_object = create_version_object(version_dictionary)
    features = version['updateFeatures']
    for feature in features:
        create_feature_objects(feature, version_object)
    return version_object


def update_version_object(request_data, version_id):
    version_object = get_version_object_by_id(version_id)
    version_object.update_type = request_data['updateType']
    version_object.created_by = request_data['username']
    version_object.save()
    update_features(version_object, request_data['updateFeatures'])
    return version_object


def update_features(version_object, features):
    [x.delete() for x in version_object.versionfeature_set.all()]
    for feature in features:
        create_feature_objects(feature, version_object)
    return version_object
