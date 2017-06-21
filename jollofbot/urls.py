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

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^messenger/buyer/?$', buyer_webhook),
    url(r'^messenger/seller/?$', seller_webhook),

    url(r'^messenger/buyer/subscribe/$', buyer_subscribe),
    url(r'^messenger/seller/subscribe/$', seller_subscribe),

    url(r'^messenger/buyer/prep/$', buyer_prep),
    url(r'^messenger/seller/prep/$', seller_prep),

    url(r'^$', show_landing),  # jollofbot.com/
    url(r'^signup/$', show_signup),
    url(r'^login/$', show_login),
    url(r'^logout/(?P<username>\w+)/$', show_logout),
    url(r'^dash/$', show_dash),
    url(r'^vendor/profile/$', show_profile),
]
