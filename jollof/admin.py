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
