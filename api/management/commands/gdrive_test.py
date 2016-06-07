# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import traceback

from django.core.management.base import BaseCommand, CommandError

from api.models import GDriveProvider
from api.clouds.gdrive import resync_from_gdrive, get_pydrive_object, update_quota, get_all_files


class Command(BaseCommand):
    help = 'Cron to update the billing for all pending jobs'

    def handle(self, *args, **options):
        try:
            prov = GDriveProvider.objects.get()
            drive = get_pydrive_object(prov)
            all_files = get_all_files(drive)

            #print all_files
            #for f in all_files:
            #    print f['id'], f['mimeType'], f['title'], f['parents']

            resync_from_gdrive(prov)

            #drive = get_pydrive_object(prov)

            #update_quota(prov, drive)


        except Exception as e:
            self.stdout.write(traceback.format_exc())

            raise CommandError(e.message)
