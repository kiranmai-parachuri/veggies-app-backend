import django;
from django.db import transaction

django.setup()
import threading
from veggies_service.services.customize_delivery_notification_cron import send_customize_delivery_notification
from veggies_service.services.place_order_notification import send_marketing_notification
from veggies_service.service_apis_handler import user_handler
from veggies_service.service_apis.otp import OTP
from veggies_service.service_apis.version import Version
from veggies_service.service_apis.ping import Ping
from veggies_service.service_apis.user import User
from veggies_service.service_apis.category import Category
from veggies_service.service_apis.slider import Slider
from veggies_service.service_apis.product import Product
from veggies_service.service_apis.pincode import Pincode
from veggies_service.service_apis.saver import Saver
from veggies_service.service_apis.basket import Basket
from veggies_service.service_apis.order import Order
from veggies_service.service_apis.address import Address
from veggies_service.service_apis.slot import Slot
from veggies_service.service_apis.delivery import Delivery
from veggies_service.service_apis.query import Query
from veggies_service.service_apis.favorite import Favorite
from veggies_service.service_apis.webhook import Webhook
from veggies_service.service_apis.default_delivery import DefaultDelivery
from veggies_service.service_apis.coupon import Coupon
from veggies_service.service_apis.price_per_point import PricePerPoint

# from veggies_service.service_apis.notification import Notification


from flask import Flask, render_template, request
from flask_restful import Api

app = Flask(__name__)
api = Api(app, prefix='/veggies/')
api.add_resource(Ping, 'ping')
api.add_resource(OTP, 'otp/')
api.add_resource(Version, 'version/')
api.add_resource(User, 'user/<mobile>/', 'user/')
api.add_resource(Category, 'category/<id>/', 'category/')
api.add_resource(Slider, 'slider/<id>/', 'slider/')
api.add_resource(Product, 'product/<id>/', 'product/')
api.add_resource(Pincode, 'pincode/<id>/', 'pincode/')
api.add_resource(Saver, 'saver/<id>/', 'saver/')
api.add_resource(Basket, 'basket/<id>/', 'basket/')
api.add_resource(DefaultDelivery, 'defaultdelivery/<id>/', 'defaultdelivery/')
api.add_resource(Order, 'order/<id>/', 'order/')
api.add_resource(Address, 'address/<id>/', 'address/')
api.add_resource(Slot, 'slot/<id>/', 'slot/')
api.add_resource(Delivery, 'delivery/<id>/', 'delivery/')
api.add_resource(Query, 'query/<id>/', 'query/')
api.add_resource(Favorite, 'favorite/<product_id>/', 'favorite/')
api.add_resource(Webhook, 'webhook/<id>/', 'webhook/')
api.add_resource(Coupon, 'coupon/<code>/', 'coupon/')
api.add_resource(PricePerPoint, 'priceperpoint/<id>/', 'priceperpoint/')


# api.add_resource(Notification, 'notification/<id>/', 'notification/')


@transaction.atomic
@app.route('/veggies/verify/')
def verify():
    data = request.args
    token = data.get('token')
    print 'token-:', token
    if token:
        user = user_handler.is_user_present_for_verification_code(token)
        if not user:
            return render_template('error.html')
        user.is_email_verified = True
        user.save()
        return render_template('success.html', data={'first_name': user.first_name,
                                                     'last_name': user.last_name})


if __name__ == '__main__':
    marketing_notification_thread = threading.Thread(target=send_marketing_notification, args=())
    customize_delivery_notification_thread = threading.Thread(target=send_customize_delivery_notification, args=())
    marketing_notification_thread.start()
    customize_delivery_notification_thread.start()
    app.run(host="127.0.0.1", port=2009, debug=True)
