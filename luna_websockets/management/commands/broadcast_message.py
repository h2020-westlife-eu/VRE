# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>


# DJANGO
from django.core.management.base import BaseCommand, CommandError
from luna_websockets.messaging import broadcast_message


class Command(BaseCommand):
    help = 'Broadcasts a message to all connected clients'

    def add_arguments(self, parser):
        parser.add_argument('topic')
        parser.add_argument('message')

    def handle(self, *args, **options):
        broadcast_message(options['topic'], options['message'])
