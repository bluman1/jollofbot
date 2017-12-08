from django.contrib import admin
from jollof.models import *
# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['fbid']


admin.site.register(Profile, ProfileAdmin)

class JollofAdmin(admin.ModelAdmin):
    list_display = ['description']


admin.site.register(Jollof, JollofAdmin)

class JollofOrderAdmin(admin.ModelAdmin):
    list_display = ['code', 'order_type']


admin.site.register(JollofOrder, JollofOrderAdmin)

class DelicacyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


admin.site.register(Delicacy, DelicacyAdmin)

class DelicacyOrderAdmin(admin.ModelAdmin):
    list_display = ['code', 'order_type']


admin.site.register(DelicacyOrder, DelicacyOrderAdmin)

class FutureLocationAdmin(admin.ModelAdmin):
    list_display = ['fbid', 'latitude', 'longitude']


admin.site.register(FutureLocation, FutureLocationAdmin)

class MeReferralAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'referral', 'source', 'type']


admin.site.register(MeReferral, MeReferralAdmin)


class BuyerConversationAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'message', 'jollof_sender', 'read', 'delivered', 'read_timestamp', 'delivered_timestamp']


admin.site.register(BuyerConversation, BuyerConversationAdmin)


class SellerConversationAdmin(admin.ModelAdmin):
    list_display = ['seller', 'message', 'jollof_sender', 'read', 'delivered', 'read_timestamp', 'delivered_timestamp']


admin.site.register(SellerConversation, SellerConversationAdmin)


class FlashConversationAdmin(admin.ModelAdmin):
    list_display = ['flash', 'message', 'jollof_sender', 'read', 'delivered', 'read_timestamp', 'delivered_timestamp']


admin.site.register(FlashConversation, FlashConversationAdmin)
