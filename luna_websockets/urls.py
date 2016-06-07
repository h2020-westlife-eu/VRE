# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>


from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_subscribed_channels/$', views.GetSubscribedChannels.as_view(), name='luna_websockets_channels'),
]
