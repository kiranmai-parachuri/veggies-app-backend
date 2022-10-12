# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-03 10:09
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veggies_models', '0025_auto_20201002_0146'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='does_have_query',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='login',
            name='token',
            field=models.CharField(default=b'6a619a3a-c76f-48ff-95b3-0712759fd9da', max_length=128),
        ),
        migrations.AlterField(
            model_name='otp',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 3, 10, 14, 45, 685674)),
        ),
        migrations.AlterField(
            model_name='otp',
            name='uuId',
            field=models.CharField(default=b'0b96a365-329d-4d3f-bc81-44fdb93b0ed5', max_length=512),
        ),
    ]