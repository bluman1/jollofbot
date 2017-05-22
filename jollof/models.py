from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Company name, Email and password are required. Other fields are optional.
    """
    username = models.CharField(
        _('user name'), max_length=128, unique=True) # company username
    email = models.EmailField(_('email address'), max_length=254, unique=True) # company email
    first_name = models.CharField(_('first name'), max_length=30, blank=True) # 
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    state = models.CharField(
        _('state'), max_length=100, blank=True)
    bank_name = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Deselect this instead of deleting accounts.'))

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


    
