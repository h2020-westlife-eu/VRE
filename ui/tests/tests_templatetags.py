# -*- coding: utf-8 -*-

# Copyright Luna Technology 2015

# DJANGO
from django.contrib.sites.models import Site
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.test import TestCase

# OUR WEBAPP
from ..templatetags import title_switcher as ts


class TemplateTagsTest(TestCase):
    def test_application_title(self):
        assert ts.application_title() == 'example.com'

        for s in Site.objects.all():
            s.delete()
        assert ts.application_title() == "West-Life"

    def test_domain_name(self):
        assert ts.domain_name() == 'example.com'

        for s in Site.objects.all():
            s.delete()
        assert ts.domain_name() == "portail.west-life.eu"

    def test_application_logo(self):
        site = Site.objects.all()[0]

        site.domain = "example.com"
        site.save()
        assert ts.application_logo() == static('img/westlife-logo.png')

        site.domain = "pypeapp.com"
        site.save()
        assert ts.application_logo() == static("img/pype.png")

    def test_application_logo_white(self):
        site = Site.objects.all()[0]

        site.domain = "example.com"
        site.save()
        assert ts.application_logo_white() == static('img/westlife-logo.png')

        site.domain = "pypeapp.com"
        site.save()
        assert ts.application_logo_white() == static("img/pype-white.png")
