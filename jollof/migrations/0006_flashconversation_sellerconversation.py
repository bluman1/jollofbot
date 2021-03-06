# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-08 14:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jollof', '0005_buyerconversation'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlashConversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(default='')),
                ('jollof_sender', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('read_timestamp', models.CharField(max_length=128)),
                ('delivered', models.BooleanField(default=False)),
                ('delivered_timestamp', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('flash', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jollof.Profile')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='SellerConversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(default='')),
                ('jollof_sender', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('read_timestamp', models.CharField(max_length=128)),
                ('delivered', models.BooleanField(default=False)),
                ('delivered_timestamp', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jollof.Profile')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]
