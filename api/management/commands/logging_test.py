# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>

import logging
import traceback

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Logging and stuff'

    def handle(self, *args, **options):

        try:
            raise RuntimeError('An exception')
        except:
            logging.exception('Caught an exception')

        logging.info('Message', extra={ "a": 1, "c": 'c'})
