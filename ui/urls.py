# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


from django.conf.urls import url, include

from . import views

westlife_pages = [
    url(r'example/$', views.westlife_static_page, { 'page_name': 'example.html'}),
]

urlpatterns = [
    url(r'^$', views.Root.as_view(), name='home'),
    url(r'^home/$', views.MainPage.as_view(), name='main'),
    url(r'^services/$', views.westlife_services, name='westlife_services'),
    url(r'^internet_explorer/', views.internet_explorer, name="internet_explorer"),
    url(r'^cgv/$', views.legal, name='cgv'),
    url(r'^build_info/$', views.BuildInfo.as_view()),
    url(r'^pages/', include(westlife_pages))
]
