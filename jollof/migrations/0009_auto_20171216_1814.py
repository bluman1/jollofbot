# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-16 17:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jollof', '0008_auto_20171208_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='delicacyorder',
            name='paid_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jolloforder',
            name='paid_status',
            field=models.BooleanField(default=False),
        ),
    ]