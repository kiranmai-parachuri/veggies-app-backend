from veggies_service.db.veggies_models.models import Category
from veggies_service.utils.exceptions import BadRequest, NotFoundException
from veggies_service.utils.file_utils import delete_file, update_file_from_request, \
    save_file_from_request
from veggies_service.views.category import CategoryView


def create_category(request, user):
    data = request.form.to_dict()
    try:
        name = data['name']
    except KeyError as k:
        raise BadRequest(errorMessage='key error:' + str(k))
    filename = save_file_from_request(request)
    category = Category.objects.create(name=name, image=filename, created_by=user)
    return category


def get_categories():
    return Category.objects.all()


def update_category(name, request):
    category = get_category_by_id(name)
    data = request.form.to_dict()
    if request.files or 'file' in data:
        category.image = update_file_from_request(request, category)
    if 'name' in data:
        category.name = data['name']
    category.save()
    return category


def get_category_by_id(id):
    try:
        category = Category.objects.get(id=id)
    except Exception as e:
        raise NotFoundException(entity='Category')
    return category


def delete_category(id):
    category = get_category_by_id(id)
    products = category.product_set.all()
    if products:
        raise BadRequest(errorMessage='Can not delete category containg products: '+','.join([p.name for p in products]))
    view = CategoryView()
    response = view.render(category)
    delete_file(category.image)
    category.delete()

    return {'category': response}
