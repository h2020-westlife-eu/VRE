# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import os
import traceback

from celery import shared_task
from django.utils.timezone import now

from api.data import (
    DATAFILE_ERROR,
    DATAFILE_READY,
    STORAGE_ACCOUNT_READY,
    STORAGE_ACCOUNT_VALIDATING,
    STORAGE_ACCOUNT_VALIDATION_FAILED
)
from api.models import Datafile, Folder, SyncOperation, UserStorageAccount

from api.clouds.s3 import check_s3_credentials, upload_file_to_s3, retrieve_file_from_s3, delete_file_from_s3
from api.clouds.gdrive import (
    check_gdrive_credentials,
    upload_file_to_gdrive,
    retrieve_file_from_gdrive,
    delete_file_from_gdrive,
    create_folder_on_gdrive,
    resync_from_gdrive
)
from api.clouds.b2drop import (
    check_b2drop_credentials,
    create_folder_on_b2drop,
    delete_file_from_b2drop,
    retrieve_file_from_b2drop,
    resync_from_b2drop,
    upload_file_to_b2drop,
)
from api.clouds.dbox import (
    check_dropbox_credentials,
    create_folder_on_dropbox,
    delete_file_from_dropbox,
    retrieve_file_from_dropbox,
    resync_from_dropbox,
    upload_file_to_dropbox,
)
from api.clouds.wl_webdav import (
    check_webdav_credentials,
    create_folder_on_webdav,
    delete_file_from_webdav,
    retrieve_file_from_webdav,
    resync_from_webdav,
    upload_file_to_webdav,
)
from api.clouds import dummy

from api.serializers import UserStorageAccountSerializer
from luna_websockets.messaging import send_message


REFRESH_INTERVAL = 15

DISPATCH_CALLS = {
    'S3_PROVIDER': {
        'upload': upload_file_to_s3,
        'check_credentials': check_s3_credentials,
        'retrieve': retrieve_file_from_s3,
        'delete': delete_file_from_s3,
        'resync': None,
        'create_folder': None,
    },
    'GDRIVE_PROVIDER': {
        'upload': upload_file_to_gdrive,
        'check_credentials': check_gdrive_credentials,
        'retrieve': retrieve_file_from_gdrive,
        'delete': delete_file_from_gdrive,
        'resync': resync_from_gdrive,
        'create_folder': create_folder_on_gdrive,
    },
    'B2DROP_PROVIDER': {
        'upload': upload_file_to_b2drop,
        'check_credentials': check_b2drop_credentials,
        'retrieve': retrieve_file_from_b2drop,
        'delete': delete_file_from_b2drop,
        'resync': resync_from_b2drop,
        'create_folder': create_folder_on_b2drop,
    },
    'WL_WEBDAV_PROVIDER': {
        'upload': upload_file_to_webdav,
        'check_credentials': check_webdav_credentials,
        'retrieve': retrieve_file_from_webdav,
        'delete': delete_file_from_webdav,
        'resync': resync_from_webdav,
        'create_folder': create_folder_on_webdav,
    },
    'DROPBOX': {
        'upload': upload_file_to_dropbox,
        'check_credentials': check_dropbox_credentials,
        'retrieve': retrieve_file_from_dropbox,
        'delete': delete_file_from_dropbox,
        'resync': resync_from_dropbox,
        'create_folder': create_folder_on_dropbox,
    },
    'DUMMY': {
        'upload': dummy.upload,
        'check_credentials': dummy.check_credentials,
        'retrieve': dummy.retrieve,
        'delete': dummy.delete,
        'resync': dummy.resync,
        'create_folder': dummy.create_folder,
    }
}


def dispatch_call(provider, call_name, *args, **kwargs):
    fun = DISPATCH_CALLS[provider.type].get(call_name, None)

    if fun is None:
        print('Call for %s on provider %s not implemented yet!' % (call_name, provider.type))
        return None

    else:
        return fun(*args, **kwargs)


@shared_task
def check_credentials(provider_pk):
    provider = UserStorageAccount.objects.get(pk=provider_pk).get_concrete()

    if provider.validation_state == STORAGE_ACCOUNT_VALIDATING:
        return
    else:
        provider.validation_state = STORAGE_ACCOUNT_VALIDATING
        provider.save()

    try:
        dispatch_call(provider, 'check_credentials', provider)
        provider.validation_state = STORAGE_ACCOUNT_READY
    except:
        traceback.print_exc()
        provider.validation_state = STORAGE_ACCOUNT_VALIDATION_FAILED
    provider.save()
    send_message(provider.owner, 'model.UserStorageAccount.updateOne', UserStorageAccountSerializer(provider).data)


@shared_task
def upload_file(datafile_pk, tempfile_path):
    try:
        datafile = Datafile.objects.get(pk=datafile_pk)
        provider = datafile.storage_account.get_concrete()

        datafile.size = os.path.getsize(tempfile_path)

        try:
            storage_key = dispatch_call(provider, 'upload', datafile, provider, tempfile_path)
            datafile.upload_state = DATAFILE_READY
            datafile.storage_key = storage_key
            print('Upload was successful!')
        except:
            datafile.upload_state = DATAFILE_ERROR
            print('Upload failed: %s' % traceback.format_exc())

        datafile.save()

    finally:
        os.remove(tempfile_path)


@shared_task
def create_folder(folder_pk):
    try:
        folder = Folder.objects.get(pk=folder_pk)
        provider = folder.storage_account.get_concrete()

        storage_key = dispatch_call(provider, 'create_folder', folder, provider)
        if storage_key is not None:
            folder.storage_key = storage_key
            folder.save()
    except Exception:
        raise


@shared_task
def retrieve_file(datafile_pk):
    try:
        datafile = Datafile.objects.get(pk=datafile_pk)
        provider = datafile.storage_account.get_concrete()

        return dispatch_call(provider, 'retrieve', datafile, provider)
    except Exception:
        raise


@shared_task
def delete_file(provider_pk, storage_key):
    """
    This function doesn't take a datafile_pk as argument because, when it runs, the Datafile has already been deleted
    :param provider_pk:
    :param storage_key:
    :return:
    """
    try:
        provider = UserStorageAccount.objects.get(pk=provider_pk).get_concrete()
        return dispatch_call(provider, 'delete', provider, storage_key)
    except Exception:
        raise


@shared_task
def resync(provider_pk):
    generic_provider = UserStorageAccount.objects.get(pk=provider_pk)

    # Check that we haven't sync just before
    last_sync_operation = SyncOperation.get_latest_for_account(generic_provider)

    # if last_sync_operation is not None and (now() - last_sync_operation.created_at).total_seconds() < REFRESH_INTERVAL:
    #     print('Last operation too recent. Not resyncing anything.')
    #     return

    if last_sync_operation is not None and last_sync_operation.ongoing:
        print('Last sync operation is still in progress.')
        return

    provider = generic_provider.get_concrete()
    sync_op = SyncOperation.objects.create(storage_account=generic_provider, ongoing=True)

    # Notify the user that the account is syncing
    send_message(provider.owner, 'model.UserStorageAccount.updateOne', UserStorageAccountSerializer(provider).data)

    try:
        dispatch_call(provider, 'resync', provider)
    finally:
        sync_op.ongoing = False
        sync_op.save()

        # In case we have updated the quota, publish it to the client
        # + signal that the sync operation is finished
        send_message(provider.owner, 'model.UserStorageAccount.updateOne', UserStorageAccountSerializer(provider).data)

