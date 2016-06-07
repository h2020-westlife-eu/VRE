# coding: utf-8

# Copyright Luna Technology 2016

# PYTHON
import os
import tempfile
import traceback

# THIRD PARTY PYTHON
from dropbox import DropboxOAuth2Flow
from dropbox.dropbox import Dropbox
from dropbox.files import FolderMetadata, WriteMode
from dropbox.oauth import (
    BadRequestException,
    BadStateException,
    CsrfException,
    NotApprovedException,
    ProviderException,
)

# DJANGO
from django.conf import settings

# OUR WEBAPP
from api.data import DATAFILE_READY
from api.models import Folder, Datafile


def get_dropbox_auth_flow(web_app_session):
    return DropboxOAuth2Flow(
        settings.DROPBOX_APP_KEY,
        settings.DROPBOX_APP_SECRET,
        settings.DROPBOX_CLIENT_REDIRECT_URI,
        web_app_session,
        "dropbox-auth-csrf-token"
    )


def dropbox_auth_start(web_app_session, url_state=None):
    authorize_url = get_dropbox_auth_flow(web_app_session).start(url_state=url_state)
    return authorize_url


def dropbox_auth_finish(web_app_session, request):
    try:
        access_token, user_id, url_state = get_dropbox_auth_flow(web_app_session).finish(request.query_params)
    except CsrfException as e:
        raise e
    except BadRequestException as e:
        raise e
    except NotApprovedException, e:
        # user did not accept dropbox integration
        return None, None, None
    except ProviderException as e:
        # Auth error in dropbox
        raise e
    except BadStateException as e:
        # Start the auth flow again.
        # redirect_to("/dropbox-auth-start")
        raise e
    except Exception as e:
        raise e
    return access_token, user_id, url_state


def get_dropbox_object(provider):
    db = Dropbox(provider.access_token)
    return db


def check_dropbox_credentials(provider):
    '''
    If this call passes, we have access to the dropbox !
    '''
    user_dropbox = get_dropbox_object(provider)
    user_dropbox.files_list_folder('')


def append_slash_at_the_beginning(path):
    '''
    To be valid, Dropbox expects '/*' paths
    '''
    return os.path.join('/', path)


def upload_file_to_dropbox(datafile, provider, tempfile_path):
    dropbox = get_dropbox_object(provider)
    path = append_slash_at_the_beginning(datafile.rel_path)
    with open(tempfile_path, 'r') as f:
        file1 = dropbox.files_upload(
            f.read(),
            path,
            mode=WriteMode('add', None),
            autorename=True,
            client_modified=None,
            mute=False
        )

    return file1.path_lower


def create_folder_on_dropbox(folder, provider):
    dropbox = get_dropbox_object(provider)
    path = append_slash_at_the_beginning(folder.rel_path)
    folder = dropbox.files_create_folder(path)
    return folder.path_lower


def retrieve_file_from_dropbox(datafile, provider):
    dropbox = get_dropbox_object(provider)

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfilename = tmpfile.name

            path = append_slash_at_the_beginning(datafile.storage_key)
            file1 = dropbox.files_download(path)
            if file1[1].status_code == 200:
                tmpfile.write(file1[1].content)

            return tmpfilename

    except:
        print('Download failed: %s' % traceback.format_exc())
        return None


def delete_file_from_dropbox(provider, storage_key):
    dropbox = get_dropbox_object(provider)

    try:
        dropbox.files_delete(storage_key)
        return True
    except:
        print('Delete failed: %s' % traceback.format_exc())
        return False


def get_children(dropbox, parent_id=None):
    # The root of a dropbox has path '', but this isn't allowed by our system
    if parent_id is None or parent_id == '/':
        parent_id = ''
    children = dropbox.files_list_folder(parent_id).entries
    return children


def update_quota(provider, dropbox):
    try:
        quota = dropbox.users_get_space_usage().used
    except:
        print('Could not get quota from Dropbox')
        traceback.print_exc()
    else:
        provider.quota_bytes = quota
        provider.save()


def resync_from_dropbox(provider):
    dropbox = get_dropbox_object(provider)

    root_folder = Folder.objects.get(storage_account=provider, parent=None)
    sync_folder_with_dropbox(dropbox, provider, root_folder)

    update_quota(provider, dropbox)


def sync_folder_with_dropbox(dropbox, provider, local_folder):
    folder_id = local_folder.storage_key

    child_folders = list(Folder.objects.filter(parent=local_folder))
    child_folders_map = {child_folder.storage_key: child_folder for child_folder in child_folders}

    child_files = list(Datafile.objects.filter(folder=local_folder))
    child_files_map = {child_file.storage_key: child_file for child_file in child_files}

    for child in get_children(dropbox, folder_id):
        if isinstance(child, FolderMetadata):
            # Check that the folder is present on both sides
            if child.id in child_folders_map.keys():
                folder = child_folders_map[child.id]
                if folder.name != child.name:
                    folder.name = child.name
                    folder.save()
                del(child_folders_map[child.id])
            else:
                # The folder isn't present locally. Create it
                folder = Folder()
                folder.owner = provider.owner
                folder.parent = local_folder
                folder.name = child.name
                folder.storage_account = provider
                folder.storage_key = child.path_lower
                folder.save()

            sync_folder_with_dropbox(dropbox, provider, folder)

        else:
            if child.id in child_files_map.keys():
                file1 = child_files_map[child.id]
                if file1.filename != child.name:
                    file1.name = child.name
                    file1.save()

                try:
                    size = int(child.size)
                except (KeyError, ValueError):
                    size = None

                if file1.size != size:
                    file1.size = size
                    file1.save()

                del(child_files_map[child.id])
            else:
                # The file isn't present locally. Create it
                file1 = Datafile()
                file1.owner = provider.owner
                file1.folder = local_folder
                file1.filename = child.name
                file1.upload_state = DATAFILE_READY
                file1.storage_key = child.path_lower
                try:
                    file1.size = int(child.size)
                except (KeyError, ValueError):
                    file1.size = None
                file1.save()

    # Do we have any files on the local side that aren't on the distant side
    # anymore?
    for rem_folder_key in child_folders_map:
        rem_folder = child_folders_map[rem_folder_key]
        rem_folder.delete()

    for rem_file_key in child_files_map:
        rem_file = child_files_map[rem_file_key]
        rem_file.delete()
