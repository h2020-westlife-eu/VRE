# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>


from django.core.management.base import BaseCommand, CommandError

from api.models import ExternalJobPortalForm


class Command(BaseCommand):
    help = 'Load initial data'

    def handle(self, *args, **options):
        ExternalJobPortalForm.load_initial()
