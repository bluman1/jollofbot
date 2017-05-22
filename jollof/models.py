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

    def get_gender(self):
        if self.gender == 2:
            return "Female"
        return "Male"


class Seller(models.Model):
    fbid = models.CharField(max_length=128, unique=True)
    company = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    gender = models.IntegerField(default=1) # 1 male 2 female
    phone_number = models.CharField(max_length=128)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Order(models.Model):
    code = models.CharField(max_length=128)
    jollof_buyer = models.ForeignKey(Buyer)
    jollof_seller = models.ForeignKey(Seller)
    status = models.IntegerField(default=0)


    
