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
            raise ValueError('The given user name must be set')
        if not email:
            raise ValueError('The given email must be set')
        username = username.strip()
        email = self.normalize_email(email)
        user = self.model(username=username,
                          email=email, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          created=now,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, email, password, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True,
                                 **extra_fields)


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
