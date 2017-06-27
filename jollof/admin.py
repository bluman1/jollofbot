from django.contrib import admin
from jollof.models import *
# Register your models here.

class BuyerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name']


admin.site.register(Buyer, BuyerAdmin)

class SellerAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'first_name', 'last_name']


admin.site.register(Seller, SellerAdmin)

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
