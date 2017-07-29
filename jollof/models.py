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
                     is_superuser, is_staff, **extra_fields):
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
                          is_superuser=is_superuser, is_staff=is_staff, last_login=now,
                          created=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True,
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
    history = models.TextField(default='')

    def get_gender(self):
        if self.gender == 2:
            return "Female"
        return "Male"
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        ordering = ['first_name', 'last_name']
    
    class Admin:
        pass


class Seller(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=128, unique=True) # seller username
    email = models.EmailField(max_length=254, unique=True) # company email
    fbid = models.CharField(max_length=128, unique=False)
    code = models.CharField(max_length=6, unique=True, default='')
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
    delivery_price = models.FloatField(default=0.0)
    available = models.BooleanField(default=True)
    average_delivery_time = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='logos', default = '/default_logo.png')
    star = models.IntegerField(default=1) #1star,3star,5star, 0star for free trial
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.restaurant
    
    def get_short_name(self):
        return self.username
        
    class Meta:
        verbose_name = _('seller')
        verbose_name_plural = _('sellers')
        ordering = ['restaurant']
    
    class Admin:
        pass


class Jollof(models.Model):
    seller = models.ForeignKey(Seller)
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.description
    
    def get_pk(self):
        return self.seller.pk

    image = models.ImageField(upload_to='jollofs', default = '/default_jollof.jpg')

    class Meta:
        ordering = ['description']
    
    class Admin:
        pass


class JollofOrder(models.Model):
    code = models.CharField(max_length=128)
    jollof_buyer = models.ForeignKey(Buyer)
    jollof_seller = models.ForeignKey(Seller)
    jollof = models.ForeignKey(Jollof, default=1)
    status = models.IntegerField(default=0) #0=pending, 1=accepted, 2=rejected, 3=cancelled, 4=completed
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order_type = models.IntegerField(default=1) # 1 = Reservation 2 = Delivery

    def __str__(self):
        return self.code + ' ' + 'Reservation' if self.order_type == 1 else 'Delivery'

    class Meta:
        ordering = ['code']


class Delicacy(models.Model):
    seller = models.ForeignKey(Seller)
    name = models.CharField(max_length=80, default='Delicacy')
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=80)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_pk(self):
        return self.seller.pk

    image = models.ImageField(upload_to='delicacies', default = '/default_delicacy.jpg')

    class Meta:
        ordering = ['name']
    
    class Admin:
        pass


class DelicacyOrder(models.Model):
    code = models.CharField(max_length=128)
    delicacy_buyer = models.ForeignKey(Buyer)
    delicacy_seller = models.ForeignKey(Seller)
    delicacy = models.ForeignKey(Delicacy)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order_type = models.IntegerField(default=1) # 1 = Reservation 2 = Delivery

    def __str__(self):
        return self.code + ' ' + 'Reservation' if self.order_type == 1 else 'Delivery'

    class Meta:
        ordering = ['code']
    
    class Admin:
        pass


class SampleFile(models.Model):
    title = models.CharField(max_length=50)
    file = models.ImageField(upload_to='samples', default = '/no-img.jpg')


class FutureLocation(models.Model):
    fbid = models.CharField(max_length=128, unique=False)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fbid

    class Meta:
        ordering = ['fbid']
    
    class Admin:
        pass
