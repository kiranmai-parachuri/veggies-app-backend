# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
# Create your models here.
from datetime import datetime, timedelta, time

from django.db import models

from veggies_service.constants.login_constants import OTP_EXPIRY_MINUTES


class Address(models.Model):
    address_line1 = models.CharField(max_length=512)
    address_line2 = models.CharField(max_length=512)
    state = models.CharField(max_length=512, null=False)
    district = models.CharField(max_length=512, null=False)
    taluka = models.CharField(max_length=512, null=False)
    village = models.CharField(max_length=512, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    pincode = models.ForeignKey('Pincode')
    location = models.CharField(max_length=512, null=True)


class User(models.Model):
    gender_choices = (('M', 'M'),
                      ('F', 'F'),
                      ('O', 'O'))
    role_choices = (('ADMIN', 'ADMIN'),
                    ('CUSTOMER', 'CUSTOMER'))
    mobile = models.CharField(max_length=12, primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=gender_choices)
    email = models.CharField(max_length=255)
    addresses = models.ManyToManyField(Address)
    does_hold_membership = models.BooleanField(default=False)
    role = models.CharField(max_length=255, choices=role_choices, default='CUSTOMER')
    created_on = models.DateTimeField(auto_now=True)
    is_email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=1024, default=str(uuid.uuid4()))
    fcm_id = models.CharField(max_length=2048, null=True)


class Slot(models.Model):
    days = (
        ('MONDAY', 0),
        ('TUESDAY', 1),
        ('WEDNESDAY', 2),
        ('THURSDAY', 3),
        ('FRIDAY', 4),
        ('SATURDAY', 5),
        ('SUNDAY', 6),
    )
    day = models.IntegerField()
    start_time = models.TimeField(default=time(9))
    end_time = models.TimeField(default=time(20))
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)


class Pincode(models.Model):
    pincode = models.IntegerField()
    delivery_charges = models.FloatField()
    slot = models.ManyToManyField(Slot)
    delivery_days = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)


class Login(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=128, default=str(uuid.uuid4()))
    otp = models.ForeignKey('OTP')
    created_on = models.DateTimeField(auto_now=True)
    logout = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)


class OTP(models.Model):
    user = models.ForeignKey(User)
    otp = models.IntegerField()
    request_id = models.CharField(max_length=512, null=True)
    uuId = models.CharField(max_length=512, default=str(uuid.uuid4()))
    expire_time = models.DateTimeField(
        default=datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES))
    created_on = models.DateTimeField(auto_now=True)


class Version(models.Model):
    UPDATE_TYPE = (('MANDATORY', "MANDATORY"),
                   ('TRIVIAL', "TRIVIAL"))

    version_name = models.CharField(max_length=128)
    update_type = models.CharField(max_length=128, choices=UPDATE_TYPE,
                                   default='TRIVIAL')
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=128, null=True)
    product = models.CharField(max_length=128)


class VersionFeature(models.Model):
    version = models.ForeignKey(Version)
    feature = models.CharField(max_length=1024, blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=1024)
    image = models.CharField(max_length=512, null=True)
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)


class Image(models.Model):
    type_choices = (('SLIDER', 'SLIDER'),
                    ('BANNER', 'BANNER'))
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=512, null=True)
    created_on = models.DateTimeField(auto_now=True)
    image_type = models.CharField(max_length=100, choices=type_choices, default='SLIDER')
    created_by = models.ForeignKey(User)


class Quantities(models.Model):
    unit_choices = (('GM', 'GM'),
                    ('KG', 'KG'),
                    ('ML', 'ML'),
                    ('LTR', 'LTR'),
                    ('PIECE', 'PIECE'))
    price = models.FloatField()
    unit = models.CharField(max_length=64, choices=unit_choices)
    quantity = models.IntegerField()


class Product(models.Model):
    unit_choices = (('GM', 'GM'),
                    ('KG', 'KG'),
                    ('ML', 'ML'),
                    ('LTR', 'LTR'),
                    ('PIECE', 'PIECE'))
    product_type = (
        ('BASKET', 'BASKET'),
        ('NORMAL', 'NORMAL'),
    )
    name = models.CharField(max_length=1024)
    image = models.CharField(max_length=1024, null=True)
    category = models.ForeignKey(Category, null=True)
    product_type = models.CharField(max_length=64, choices=product_type, default='NORMAL')
    description = models.TextField(null=True)
    health_benefits = models.TextField(null=True)
    mrp = models.FloatField(null=True)
    price = models.FloatField(null=True)
    nutrition_benefits = models.TextField(null=True)
    unit = models.CharField(max_length=64, choices=unit_choices, null=True)
    in_stock = models.BooleanField(default=True)
    total_quantity = models.FloatField(null=True)
    show = models.BooleanField(default=True)
    plan_details = models.ForeignKey(Quantities, related_name='plan_details', null=True)
    quantities = models.ManyToManyField(Quantities)
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)


class Basket(models.Model):
    name = models.CharField(max_length=1024)
    image = models.CharField(max_length=1024, null=True)
    points = models.IntegerField()
    price = models.FloatField()
    deliveries = models.IntegerField()
    description = models.TextField(null=True)
    products = models.ManyToManyField(Product)
    is_one_time_delivery = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now=True)
    show = models.BooleanField(default=True)
    default_delivery = models.ForeignKey('DefaultDelivery', null=True)
    created_by = models.ForeignKey(User)


class Saver(models.Model):
    type_choices = (('DAY', 'DAY'),
                    ('MONTH', 'MONTH'))
    saver_type = models.CharField(max_length=100, choices=type_choices, default='WEEK')
    product = models.ForeignKey(Product)
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User)

    class Meta:
        unique_together = (('saver_type', 'product'),)


class OrderItem(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.ForeignKey(Quantities)
    order_quantity = models.IntegerField()
    amount = models.FloatField(null=True)
    created_on = models.DateTimeField(auto_now=True)


class Order(models.Model):
    status = (
        ('CREATED', 'CREATED'),
        ('SUCCESS', 'SUCCESS'),
        ('FAIL', 'FAIL'),
        ('HOLD', 'HOLD'),
    )
    order_type = (
        ('ONE_TIME_BASKET', 'ONE_TIME_BASKET'),
        ('BASKET', 'BASKET'),
        ('NORMAL', 'NORMAL'),
    )
    delivery_status = (
        ('CONFIRMED', 'CONFIRMED'),
        ('DELIVERED', 'DELIVERED'),
        ('NOT_DELIVERED', 'NOT_DELIVERED'),
    )
    items = models.ManyToManyField(OrderItem)
    with_basket_delivery = models.BooleanField(default=False)
    basket = models.ForeignKey(Basket, null=True)
    order_type = models.CharField(max_length=128, default='NORMAL')
    total_amount = models.FloatField()
    status = models.CharField(max_length=64, choices=status, default='CREATED')
    created_on = models.DateTimeField(auto_now=True)
    order_id = models.CharField(max_length=1024, null=True)
    order_response = models.TextField()
    deliveries = models.ManyToManyField('Delivery')
    payment_id = models.CharField(max_length=1024, null=True)
    created_by = models.ForeignKey(User)
    does_have_query = models.BooleanField(default=False)
    address = models.ForeignKey(Address, null=True)
    coupon = models.ForeignKey('Coupon', null=True)
    extended_delivery = models.ForeignKey('Delivery', related_name='extended_delivery', null=True)
    delivery_status = models.CharField(max_length=512, choices=delivery_status, default='CONFIRMED')
    slot = models.ForeignKey(Slot, related_name='slot_for_deliveries', null=True)


class Delivery(models.Model):
    delivery_status = (
        ('SCHEDULED', 'SCHEDULED'),
        ('EDITABLE', 'EDITABLE'),
        ('FREEZE', 'FREEZE'),
        ('DELIVERED', 'DELIVERED'),
        ('NOT_DELIVERED', 'NOT_DELIVERED'),
    )
    user = models.ForeignKey(User)
    max_points = models.IntegerField()
    used_points = models.IntegerField(default=0)
    basket = models.ForeignKey(Basket)
    products = models.ManyToManyField(OrderItem)
    delivery_date = models.DateTimeField(null=True)
    delivery_no = models.IntegerField()
    created_on = models.DateTimeField(auto_now=True)
    slot = models.ForeignKey(Slot, null=True)
    is_default_delivery = models.BooleanField(default=False)
    address_for_delivery = models.ForeignKey(Address, related_name='delivery_address_here')
    extra_products = models.ManyToManyField(OrderItem, related_name='extra_products')
    status = models.CharField(max_length=128, choices=delivery_status, default='SCHEDULED')
    is_extra_paid_delivery = models.BooleanField(default=False)
    deliveries_done = models.BooleanField(default=False)


class DefaultDelivery(models.Model):
    products = models.ManyToManyField(OrderItem)
    points = models.IntegerField(null=True)
    used_points = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now=True)


class OrderQuery(models.Model):
    order = models.ForeignKey(Order)
    message = models.TextField()
    sender = models.ForeignKey(User)
    receiver = models.ForeignKey(User, related_name='receiver')
    created_on = models.DateTimeField(auto_now=True)


class Favorite(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    created_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("user", "product"),)


class PaymentEvents(models.Model):
    order = models.ForeignKey(Order)
    info = models.TextField()
    event = models.CharField(max_length=1024)


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10, primary_key=True)
    apply_count = models.IntegerField()
    price = models.FloatField()
    remaining_count = models.IntegerField()
    created_on = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey(User)
    is_deleted = models.BooleanField(default=False)


class CouponAvail(models.Model):
    coupon = models.ForeignKey(Coupon)
    user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now=True)


class PricePerPoint(models.Model):
    price = models.FloatField()
    user = models.ForeignKey(User)
    updated_on = models.DateTimeField(auto_now_add=True)
#
# class Notification(models.Model):
#     label = models.CharField(max_length=2048)
#     customer = models.ForeignKey(User)
#     details = models.TextField(null=True)
#     image = models.CharField(max_length=1024, null=True)
#     is_seen = models.BooleanField(default=False)
#     created_on = models.DateTimeField(auto_now=True)
