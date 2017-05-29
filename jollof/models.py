import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class Buyer(models.Model):
    fbid = models.CharField(max_length=128, unique=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    gender = models.IntegerField(default=1) # 1 male 2 female
    phone_number = models.CharField(max_length=128)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    current_state = models.CharField(max_length=128, default='DEFAULT')

    def get_gender(self):
        if self.gender == 2:
            return "Female"
        return "Male"


class Seller(models.Model):
    fbid = models.CharField(max_length=128, unique=True)
    restaurant = models.CharField(max_length=128, default='')
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    gender = models.IntegerField(default=1) # 1 male 2 female
    phone_number = models.CharField(max_length=128)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    current_state = models.CharField(max_length=128, default='DEFAULT')
    opening_hour = models.IntegerField(default=0)
    closing_hour = models.IntegerField(default=1)
    start_day = models.IntegerField(default=1) # Monday
    end_day = models.IntegerField(default=7) # Sunday


class Jollof(models.Model):
    seller = models.ForeignKey(Seller)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class JollofOrder(models.Model):
    code = models.CharField(max_length=128)
    jollof_buyer = models.ForeignKey(Buyer)
    jollof_seller = models.ForeignKey(Seller)
    jollof = models.ForeignKey(Jollof, default=1)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class JollofCode(models.Model):
    code = models.CharField(max_length=6)
    seller = models.ForeignKey(Seller)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Delicacy(models.Model):
    seller = models.ForeignKey(Seller)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=80)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class DelicacyOrder(models.Model):
    code = models.CharField(max_length=128)
    delicacy_buyer = models.ForeignKey(Buyer)
    delicacy_seller = models.ForeignKey(Seller)
    delicacy = models.ForeignKey(Delicacy)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
