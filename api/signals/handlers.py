# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from luna_websockets.messaging import send_message

from api.models import Folder, ExternalJobPortalSubmissionStateChange, UserStorageAccount
from api.serializers import ExternalJobPortalSubmissionSerializer
from api.tasks import create_folder


@receiver(post_save, sender=UserStorageAccount)
def create_root_folder_for_storage_account(sender, instance, **kwargs):
    """
    Create an associated root folder when a storage account is created
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.validated:
        if not Folder.objects.filter(parent=None, storage_account=instance).exists():
            # We need to create a root folder for the newly created storage account
            f = Folder()
            f.owner = instance.owner
            f.parent = None
            f.name = instance.display_name
            f.storage_account = instance
            f.storage_key = instance.root_folder_key
            f.save()


# We need to manually connect the signal to all subclasses of UserStorageAccount
for subclass in UserStorageAccount.__subclasses__():
    post_save.connect(create_root_folder_for_storage_account, subclass)


@receiver(pre_delete, sender=UserStorageAccount)
def delete_root_folder_for_storage_account(sender, instance, **kwargs):
    """
    Delete the associated root folder when a storage account is deleted
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    try:
        folder = Folder.objects.get(parent=None, storage_account=instance)
        folder.delete()
    except Folder.DoesNotExist:
        pass

for subclass in UserStorageAccount.__subclasses__():
    pre_delete.connect(delete_root_folder_for_storage_account, subclass)


@receiver(post_save, sender=Folder)
def create_folder_on_provider(sender, instance, **kwargs):
    """
    Queue creation of a folder on the remote side when it is created locally
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    created = kwargs['created']

    # Only trigger creation in case the folder doesn't already have an associated storage_key
    if created and instance.storage_key == '':
        create_folder.delay(instance.pk)


@receiver(post_save, sender=ExternalJobPortalSubmissionStateChange)
def notify_externaljobportalsubmission_state_change(sender, instance, **kwargs):
    """
    Notifies the user via websockets when an ExternalJobPortalSubmission state changes
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    created = kwargs['created']

    if created:
        externaljobportalsubmission = instance.external_submission
        send_message(
                externaljobportalsubmission.owner,
                'model.ExternalJobPortalSubmission.updateOne',
                ExternalJobPortalSubmissionSerializer(externaljobportalsubmission).data
        )
