# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-27 13:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jollof', '0015_auto_20170916_0250'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fbid', models.CharField(max_length=128, unique=True)),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('gender', models.IntegerField(default=1)),
                ('phone_number', models.CharField(max_length=128)),
                ('longitude', models.FloatField(default=0.0)),
                ('latitude', models.FloatField(default=0.0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('current_state', models.CharField(default='DEFAULT', max_length=128)),
                ('location_history', models.TextField(default='')),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
            },
        ),
        migrations.AddField(
            model_name='delicacyorder',
            name='delicacy_flash',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='jollof.Flash'),
        ),
        migrations.AddField(
            model_name='jolloforder',
            name='jollof_flash',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='jollof.Flash'),
        ),
    ]
