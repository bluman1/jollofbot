# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-14 20:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jollof', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='fbid',
            field=models.CharField(max_length=128),
        ),
    ]
