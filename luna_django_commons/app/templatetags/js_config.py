# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import json

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def js_config():
    return '<script type="application/json" id="js_config">%s</script>' % json.dumps(settings.JS_CONFIG)

