import datetime
import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


USER_TYPE_CHOICES = (
    ('s', 'Seller'),
    ('b', 'Buyer'),
    ('f', 'Flash'),
)

REFERRAL_TYPE_CHOICES = (
    ('n', 'New User'),
    ('o', 'Old User'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fbid = models.CharField(max_length=128)
    gender = models.IntegerField(default=1)  # 1 male 2 female
    phone_number = models.CharField(max_length=128)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    current_state = models.CharField(max_length=128, default='DEFAULT')
    location_history = models.TextField(default='')
    available = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=20, default='s', choices=USER_TYPE_CHOICES)

    has_order = models.BooleanField(default=False)

    code = models.CharField(max_length=6, default='')
    restaurant = models.CharField(max_length=128, default='')
    opening_hour = models.IntegerField(default=0)
    closing_hour = models.IntegerField(default=1)
    start_day = models.IntegerField(default=1)  # Monday
    end_day = models.IntegerField(default=7)  # Sunday
    delivers = models.BooleanField(default=False)
    delivery_price = models.FloatField(default=0.0)
    average_delivery_time = models.IntegerField(default=0)
    logo = models.ImageField(upload_to='logos', default='/default_logo.png')
    star = models.IntegerField(default=1)  # 1star,3star,5star, 0star for free trial
    vendor_balance = models.FloatField(default=0.0)
    can_withdraw = models.BooleanField(default=False)

    month_orders = models.IntegerField(default=0)

    flash_code = models.CharField(max_length=9, default='')
    flash_balance = models.FloatField(default=0.0)
    flash_fee = models.FloatField(default=0.0)
    

    def get_gender(self):
        if self.gender == 2:
            return "Female"
        return "Male"
    
    class Admin:
        pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Jollof(models.Model):
    seller = models.ForeignKey(Profile, related_name='Seller')
    price = models.FloatField(default=0.0)
    description = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.description
    
    def get_pk(self):
        return self.seller.pk

    image = models.ImageField(upload_to='jollofs', default='/default_jollof.jpg')
    
    class Admin:
        pass


class JollofOrder(models.Model):
    code = models.CharField(max_length=128)
    jollof_buyer = models.ForeignKey(Profile, related_name='Jollof_Buyer')
    jollof_seller = models.ForeignKey(Profile, related_name='Jollof_Seller')
    jollof_flash = models.ForeignKey(Profile, related_name='Jollof_Flash', null=True, blank=True)
    jollof = models.ForeignKey(Jollof, related_name='Order_Jollof')
    quantity = models.IntegerField(default=1)
    status = models.IntegerField(default=0)  # 0=pending, 1=accepted, 2=rejected, 3=cancelled, 4=completed/packaged
    flash_status = models.IntegerField(default=0)  # 0=pending, 1=accepted, 2=rejected, 3=picked_up, 4=dropped_off
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order_type = models.IntegerField(default=1)  # 1 = Reservation 2 = Delivery
    paid_status = models.BooleanField(default=False)

    def __str__(self):
        return self.code + ' ' + 'Reservation' if self.order_type == 1 else 'Delivery'

    def is_complete(self):
        return True if self.status == 4 and self.flash_status == 4 else False

    class Meta:
        ordering = ['code']


class Delicacy(models.Model):
    seller = models.ForeignKey(Profile, related_name='Delicacy_Seller')
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

    image = models.ImageField(upload_to='delicacies', default='/default_delicacy.jpg')
    
    class Admin:
        pass


class DelicacyOrder(models.Model):
    code = models.CharField(max_length=128)
    delicacy_buyer = models.ForeignKey(Profile, related_name='DelicacyBuyer')
    delicacy_seller = models.ForeignKey(Profile, related_name='DelicacySeller')
    delicacy_flash = models.ForeignKey(Profile, related_name='DelicacyFlash', null=True, blank=True)
    delicacy = models.ForeignKey(Delicacy, related_name='Order_Delicacy')
    quantity = models.IntegerField(default=1)
    status = models.IntegerField(default=0)
    flash_status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order_type = models.IntegerField(default=1)  # 1 = Reservation 2 = Delivery
    paid_status = models.BooleanField(default=False)

    def __str__(self):
        return self.code + ' ' + 'Reservation' if self.order_type == 1 else 'Delivery'

    def is_complete(self):
        return True if self.status == 4 and self.flash_status == 4 else False

    class Meta:
        ordering = ['code']
    
    class Admin:
        pass


class SampleFile(models.Model):
    title = models.CharField(max_length=50)
    file = models.ImageField(upload_to='samples', default='/no-img.jpg')


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


class MeReferral(models.Model):
    buyer = models.ForeignKey(Profile)
    referral = models.CharField(max_length=128)
    source = models.CharField(max_length=128)
    type = models.CharField(
        max_length=20, default='n', choices=REFERRAL_TYPE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['referral']
    
    class Admin:
        pass


class BuyerConversation(models.Model):
    mid = models.CharField(max_length=128, null=True)
    buyer = models.ForeignKey(Profile)
    message = models.TextField(default='')
    jollof_sender = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    read_timestamp = models.CharField(max_length=128)
    delivered = models.BooleanField(default=False)
    delivered_timestamp = models.CharField(max_length=128)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
    
    class Admin:
        pass


class SellerConversation(models.Model):
    mid = models.CharField(max_length=128, null=True)
    seller = models.ForeignKey(Profile)
    message = models.TextField(default='')
    jollof_sender = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    read_timestamp = models.CharField(max_length=128)
    delivered = models.BooleanField(default=False)
    delivered_timestamp = models.CharField(max_length=128)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
    
    class Admin:
        pass


class JollofSellerConversation(models.Model):
    order = models.ForeignKey(JollofOrder)
    conversation = models.ForeignKey(SellerConversation)
    stage = models.IntegerField(default=1)  # 1-accept/reject, 2-complete/cancel

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
    
    class Admin:
        pass


class DelicacySellerConversation(models.Model):
    order = models.ForeignKey(DelicacyOrder)
    conversation = models.ForeignKey(SellerConversation)
    stage = models.IntegerField(default=1)  # 1-accept/reject, 2-complete/cancel

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
    
    class Admin:
        pass


class FlashConversation(models.Model):
    mid = models.CharField(max_length=128, null=True)
    flash = models.ForeignKey(Profile)
    message = models.TextField(default='')
    jollof_sender = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    read_timestamp = models.CharField(max_length=128)
    delivered = models.BooleanField(default=False)
    delivered_timestamp = models.CharField(max_length=128)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
    
    class Admin:
        pass

class JollofFlashConversation(models.Model):
    order = models.ForeignKey(JollofOrder)
    conversation = models.ForeignKey(FlashConversation)
    stage = models.IntegerField(default=1)  # 1-to_pickup, 2-to_drop_off

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
    
    class Admin:
        pass


class DelicacyFlashConversation(models.Model):
    order = models.ForeignKey(DelicacyOrder)
    conversation = models.ForeignKey(FlashConversation)
    stage = models.IntegerField(default=1)  # 1-to_pickup, 2-to_drop_off

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
    
    class Admin:
        pass