from django.db.models import Q

from veggies_service.constants import user_role
from veggies_service.db.veggies_models.models import OrderQuery
from veggies_service.service_apis_handler import user_handler, order_handler
from veggies_service.utils.exceptions import BadRequest


def create_query(data, user):
    order_data = {'sender': user}
    try:
        order = order_handler.get_order_by_id(data['order'])

        order_data['order'] = order
        if user.role == user_role.ADMIN:
            order_data['receiver'] = order.created_by
        else:
            users, _ = user_handler.get_user_by_filter({'role': user_role.ADMIN})
            if users:
                order_data['receiver'] = users[0]
            else:
                raise Exception()
            order.does_have_query = True
            order.save()
        order_data['message'] = data['message']

    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    return OrderQuery.objects.create(**order_data)


def get_queries_by_filter(data, user):
    query_set = OrderQuery.objects.filter(Q(receiver=user) | Q(sender=user))
    if 'orderId' in data:
        query_set = query_set.filter(order_id=data['orderId'])
    return query_set.order_by('-id')


def mark_query_read(query_set, user):
    if user.role == user_role.ADMIN:
        for query in query_set:
            order = query.order
            order.does_have_query = False
            order.save()


def get_order_with_new_queries_for_admin(user):
    return OrderQuery.objects.filter(receiver=user, order__does_have_query=True)


def get_read_orders_for_admin(user):
    return OrderQuery.objects.filter(receiver=user, order__does_have_query=False)
