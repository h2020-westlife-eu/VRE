# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


# THIRD PARTY APP
from djng.forms import NgModelFormMixin, NgFormValidationMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3ModelForm


class AngularFormMixin(NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    required_css_class = "required"


class AngularModelFormMixin(NgModelFormMixin, NgFormValidationMixin, Bootstrap3ModelForm):
    required_css_class = "required"
