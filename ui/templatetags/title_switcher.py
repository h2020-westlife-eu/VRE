# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static

from django.contrib.sites.models import Site


register = template.Library()


@register.simple_tag
def application_title():
    try:
        return Site.objects.get_current().name
    except:
        return "West-Life"


@register.simple_tag
def domain_name():
    try:
        return Site.objects.get_current().domain
    except:
        return 'portail.west-life.eu'


@register.simple_tag
def application_logo():
    try:
        domain = Site.objects.get_current().domain
        if "pype" in domain:
            return static('img/pype.png')
        elif "symhub" in domain:
            return static('img/symhub.png')
        elif "west-life" in domain:
            return static('img/westlife-logo.png')
        else:
            return static('img/westlife-logo.png')
    except:
        return static('img/westlife-logo.png')


@register.simple_tag
def application_logo_white():
    try:
        domain = Site.objects.get_current().domain
        if "pype" in domain:
            return static('img/pype-white.png')
        elif "symhub" in domain:
            return static('img/symhub-white.png')
        elif "west-life" in domain:
            return static('img/westlife-logo.png')
        else:
            return static('img/westlife-logo.png')
    except:
        return static('img/westlife-logo.png')
