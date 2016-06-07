# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>


# DJANGO
from django.core.management.base import BaseCommand, CommandError
from luna_websockets.server.server import run_server


class Command(BaseCommand):
    help = 'Run the websockets server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--django_host',
            default='http://127.0.0.1:8000',
            help='The base url where the django app lives')

        parser.add_argument(
            '--listen_address',
            default='127.0.0.1')

        parser.add_argument(
            '--listen_port',
            default=22000,
            type=int)

        parser.add_argument(
            '--unix_socket',
            default=None)

        parser.add_argument(
            '--socket_mode',
            default='600',
        )

        parser.add_argument(
            '--socket_group',
            default=None,
        )

    def handle(self, *args, **options):
        socket_mode = int(options['socket_mode'], 8)
        run_server(
            django_host=options['django_host'],
            listen_address=options['listen_address'],
            listen_port=options['listen_port'],
            unix_socket=options['unix_socket'],
            socket_mode=socket_mode,
            socket_group=options['socket_group']
        )
