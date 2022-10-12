from marshmallow import fields

from veggies_service.constants.file_constats import SERVER_URL, DOWNLOAD_PATH
from veggies_service.utils.string_utils import string_unmarshal
from veggies_service.views.base_schema import SchemaRender, DateTimeEpoch
from veggies_service.views.category import CategoryView


class QuantityView(SchemaRender):
    id = fields.Integer()
    price = fields.Float()
    unit = fields.String()
    quantity = fields.Integer()


class QuantityPointsView(SchemaRender):
    id = fields.Integer()
    price = fields.Integer(dump_to='points')
    unit = fields.String()
    quantity = fields.Integer()


class ProductSmallView(SchemaRender):
    id = fields.Integer()
    name = fields.String()
    category = fields.Nested(CategoryView)
    image = fields.Method('get_image_url')
    price = fields.Float()
    mrp = fields.Float()
    description = fields.String()
    unit = fields.String()
    in_stock = fields.Boolean(dump_to='inStock')
    show = fields.Boolean()

    def get_image_url(self, obj):
        if obj.image:
            return SERVER_URL + DOWNLOAD_PATH + obj.image
        else:
            return ''


class ProductView(ProductSmallView):
    created_on = DateTimeEpoch(dump_to='createdOn')
    created_by = fields.Method('get_created_by')
    health_benefits = fields.Method('get_health_benefits', dump_to='healthBenefits')
    nutrition_benefits = fields.Method('get_nutrition_benefits', dump_to='nutritionBenefits')
    total_quantity = fields.Method('get_total_quantity', dump_to='totalQuantity')
    plan_details = fields.Nested(QuantityPointsView, dump_to='planDetails')
    quantities = fields.Method('get_quantities')
    product_type = fields.String(dump_to='type')

    def get_total_quantity(self, obj):
        return obj.total_quantity

    def get_quantities(self, obj):
        v = QuantityView()
        return [v.render(o) for o in obj.quantities.all()]

    def get_health_benefits(self, obj):
        return string_unmarshal(obj.health_benefits)

    def get_nutrition_benefits(self, obj):
        return string_unmarshal(obj.nutrition_benefits)

    def get_created_by(self, obj):
        return obj.created_by.first_name + ' ' + obj.created_by.last_name


if __name__ == '__main__':
    import django;

    django.setup()
    from veggies_service.db.veggies_models.models import Product

    prod = Product.objects.first()
    v = ProductView()
    print v.render(prod)
