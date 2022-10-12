from veggies_service.db.veggies_models.models import Version, VersionFeature
from veggies_service.utils.exceptions import NotFoundException


def get_version_objects_after(current_version, product_name):
    try:
        version_objects = Version.objects.filter(
            product=product_name).order_by('-created_on').prefetch_related(
            'versionfeature_set')
        to_return_version_objects = []
        print
        for v in version_objects:
            if map(lambda x: int(x), v.version_name.split('.')) > map(
                    lambda x: int(x), current_version.split('.')):
                to_return_version_objects.append(v)
        return to_return_version_objects
    except:
        raise NotFoundException(entity="Version")


def create_version_object(dictionary):
    version_object = Version.objects.create(**dictionary)
    return version_object


def create_feature_objects(feature, version_object):
    feature_object = VersionFeature.objects.create(version=version_object,
                                                   feature=feature)
    return feature_object


def get_version_object_by_id(version_id):
    try:
        version_object = Version.objects.get(id=version_id)
        return version_object
    except:
        raise NotFoundException(entity="Version")
