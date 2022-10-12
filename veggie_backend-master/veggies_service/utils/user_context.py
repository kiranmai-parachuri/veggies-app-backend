from veggies_service.constants import user_role
from veggies_service.db.veggies_models.models import Login
from veggies_service.utils.exceptions import UnauthorisedException, NotFoundException
from veggies_service.views.user import UserBasicView


def is_logged_in_user_admin(token):
    login_object = Login.objects.filter(token=token, is_active=True, user__role=user_role.ADMIN).last()
    return login_object


def is_logged_in_user_customer(token):
    login_object = Login.objects.filter(token=token, is_active=True, user__role=user_role.CUSTOMER).last()
    return login_object


def get_user_role(token):
    login_object = Login.objects.filter(token=token, is_active=True).last()
    print '---', login_object.user.mobile
    if login_object:
        return login_object.user.role
    else:
        raise UnauthorisedException()


def get_user_context(token):
    try:
        login_object = Login.objects.filter(token=token).last()
    except Exception as e:
        raise UnauthorisedException(entity='Login')
    view = UserBasicView()
    return view.render(login_object.user)


def get_user_object(token):
    login_object = Login.objects.filter(token=token, is_active=True).last()
    if login_object:
        return login_object.user
    else:
        raise NotFoundException(entity='User')


if __name__ == '__main__':
    import django;

    django.setup()

    print(get_user_context('e1bc5941-4b33-4afb-ad8b-b98d2336bf0c'))
