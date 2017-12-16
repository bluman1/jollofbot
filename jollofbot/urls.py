"""jollofbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from jollof.views import *

admin.autodiscover()
urlpatterns = [
    url(r'^c0mpl1c4t3d/', admin.site.urls),
    url(r'^bot/$', landbot),
    url(r'^f4k3/fl4sh/(?P<flash_name>\w+)/$', create_fake_flash),

    url(r'^pay/$', pay_now),
    url(r'^thankyou/$', thank_you),
    url(r'^failed/$', payment_failed),

    url(r'^messenger/buyer/?$', buyer_webhook),
    url(r'^messenger/seller/?$', seller_webhook),
    url(r'^messenger/deliver/?$', deliver_webhook),

    url(r'^messenger/buyer/subscribe/$', buyer_subscribe),
    url(r'^messenger/seller/subscribe/$', seller_subscribe),
    url(r'^messenger/deliver/subscribe/$', deliver_subscribe),

    url(r'^messenger/buyer/prep/$', buyer_prep),
    url(r'^messenger/seller/prep/$', seller_prep),
    url(r'^messenger/deliver/prep/$', deliver_prep),

    url(r'^$', show_landing),  # jollofbot.com/
    url(r'^vendor/signup/$', show_signup),
    url(r'^vendor/login/$', show_login),
    url(r'^vendor/logout/$', show_logout),
    url(r'^dash/$', show_dash),
    url(r'^vendor/$', show_vendor),
    url(r'^vendor/overview/$', show_overview),
    url(r'^vendor/profile/$', show_profile),
    url(r'^vendor/jollof/$', show_jollof),
    url(r'^vendor/delicacies/$', show_delicacies),
    url(r'^vendor/reservations/jollof/$', show_jollof_reservations),
    url(r'^vendor/deliveries/jollof/$', show_jollof_deliveries),
    url(r'^vendor/reservations/delicacy/$', show_delicacy_reservations),
    url(r'^vendor/deliveries/delicacy/$', show_delicacy_deliveries),

    url(r'^upload/$', show_test_upload),
]
