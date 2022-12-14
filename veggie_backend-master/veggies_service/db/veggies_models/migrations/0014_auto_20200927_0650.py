# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-27 06:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veggies_models', '0013_auto_20200927_0648'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_id',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='login',
            name='token',
            field=models.CharField(default=b'ffdb5e9b-bbb6-48e5-9a24-182b82af53ad', max_length=128),
        ),
        migrations.AlterField(
            model_name='otp',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 27, 6, 55, 29, 974058)),
        ),
        migrations.AlterField(
            model_name='otp',
            name='uuId',
            field=models.CharField(default=b'd53f1102-b7b2-4854-a5a4-d5e6fbe25c2b', max_length=512),
        ),
    ]
