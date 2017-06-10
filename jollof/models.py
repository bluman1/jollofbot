import datetime
import random
import string

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password,
                     is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given company name must be set')
        if not email:
            raise ValueError('The given email must be set')
        username = username.strip()
        email = self.normalize_email(email)
        user = self.model(username=username,
                          email=email, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          created=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True,
                                 **extra_fields)


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
    has_order = models.BooleanField(default=False)

    def get_gender(self):
        if self.gender == 2:
            return "Female"
        return "Male"


class Seller(models.Model):
    username = models.CharField(max_length=128, unique=True) # seller username
    email = models.EmailField(max_length=254, unique=True) # company email
    fbid = models.CharField(max_length=128, unique=True)
    code = models.CharField(max_length=6, unique=True)
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
    delivers = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('seller')
        verbose_name_plural = _('sellers')


class Jollof(models.Model):
    seller = models.ForeignKey(Seller)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)


class JollofOrder(models.Model):
    code = models.CharField(max_length=128)
    jollof_buyer = models.ForeignKey(Buyer)
    jollof_seller = models.ForeignKey(Seller)
    jollof = models.ForeignKey(Jollof, default=1)
    status = models.IntegerField(default=0) #0=pending, 1=accepted, 2=rejected, 3=cancelled, 4=completed
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order_type = models.IntegerField(default=1) # 1 = Reservation 2 = Delivery


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
    order_type = models.IntegerField(default=1) # 1 = Reservation 2 = Delivery
