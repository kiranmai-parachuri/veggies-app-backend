from veggies_service.db.veggies_models.models import Favorite
from veggies_service.service_apis_handler import product_handler
from veggies_service.utils.exceptions import AlreadyExist, BadRequest, NotFoundException
from veggies_service.views.favorite import FavoriteView


def create_favorite(data, user):
    try:
        product = product_handler.get_product_by_id(data['product'])
        try:
            favorite = Favorite.objects.create(user=user, product=product)
        except Exception as e:
            raise AlreadyExist(entity='Favorite')
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    return favorite


def delete_favorite(product_id, user):
    try:
        favorite_object = Favorite.objects.get(product_id=product_id, user=user)
    except Exception as e:
        raise NotFoundException(entity='Favorite')
    view = FavoriteView()
    res = view.render(favorite_object)
    favorite_object.delete()
    return {'favorite': res}


def get_favorite_by_filter(criteria):
    return Favorite.objects.filter(**criteria)
