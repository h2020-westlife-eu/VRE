"""pype URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('ui.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('djoser.urls.authtoken')),
    url(r'^_ws/', include('luna_websockets.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]

# adding default test user
from django.contrib.auth.models import User

if not (User.objects.filter(username='vagrant').exists()):
    try:
       user = User.objects.create_user('vagrant', 'vagrant@vagrant', 'vagrant')
       user = User.objects.create_user('vagrant2', 'vagrant2@vagrant', 'vagrant')
    except:
       print "user created, warning some error", sys.exc_info()[0]

       # urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
