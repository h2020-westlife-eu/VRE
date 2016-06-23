# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import os
import tempfile
import traceback

from apiclient.discovery import build
import httplib2
from oauth2client import client

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from django.conf import settings

from api.data import DATAFILE_READY
from api.models import Folder, Datafile

SCOPES = 'https://www.googleapis.com/auth/drive'
# CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')
APPLICATION_NAME = 'Pype (dev)'
REDIRECT_URI = 'http://dev.pype.com:8000/api/gdriveproviders/confirm_link.json/'

AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"


FOLDER_MIMETYPE = "application/vnd.google-apps.folder"


def get_flow(state=None):

    client_id = settings.GOOGLE_DRIVE_CLIENT_ID
    client_secret = settings.GOOGLE_DRIVE_CLIENT_SECRET
    redirect_uri = settings.GOOGLE_DRIVE_CLIENT_URI

    flow = client.OAuth2WebServerFlow(
        client_id,
        client_secret=client_secret,
        scope=SCOPES,
        redirect_uri=redirect_uri,
        auth_uri=AUTH_URI,
        token_uri=TOKEN_URI
    )

    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'

    if state is not None:
        flow.params['state'] = state

    return flow


def step1_get_authorize_url(state=None):
    flow = get_flow(state=state)
    auth_uri = flow.step1_get_authorize_url()

    return auth_uri


def step2_redeem_code_for_credentials(code):
    flow = get_flow()
    credentials = flow.step2_exchange(code)

    return credentials.to_json()


def step3_get_drive_service(credentials_json):
    credentials = client.OAuth2Credentials.from_json(credentials_json)
    http_auth = credentials.authorize(httplib2.Http())

    drive_service = build('drive', 'v2', http=http_auth)

    return drive_service


def get_pydrive_object(provider):
    credentials = client.OAuth2Credentials.from_json(provider.credentials)

    gauth = GoogleAuth()
    gauth.credentials = credentials

    if gauth.access_token_expired:
        print('Google Drive token expired. Refreshing...')
        gauth.Refresh()
        provider.credentials = gauth.credentials.to_json()
        provider.save()

    gauth.Authorize()

    drive = GoogleDrive(gauth)

    return drive


def check_gdrive_credentials(provider):
    drive = get_pydrive_object(provider)

    drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()


def upload_file_to_gdrive(datafile, provider, tempfile_path):
    drive = get_pydrive_object(provider)

    file1 = drive.CreateFile({
        'title': datafile.filename,
        'parents': [{'id': datafile.folder.storage_key}]
    })
    file1.SetContentFile(tempfile_path)
    file1.Upload()

    return file1['id']


def create_folder_on_gdrive(folder, provider):
    drive = get_pydrive_object(provider)

    file1 = drive.CreateFile({
        'title': folder.name,
        'mimeType': FOLDER_MIMETYPE,
        'parents': [{'id': folder.parent.storage_key}]
    })
    file1.Upload()

    return file1['id']


def retrieve_file_from_gdrive(datafile, provider):
    drive = get_pydrive_object(provider)

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfilename = tmpfile.name

            print('Using storage_key: %s' % datafile.storage_key)
            file1 = drive.CreateFile({'id': datafile.storage_key})
            print('Detected title is: %s' % file1['title'])
            file1.GetContentFile(tmpfilename)

            return tmpfilename

    except:
        print('Download failed: %s' % traceback.format_exc())
        return None


def delete_file_from_gdrive(provider, storage_key):
    drive = get_pydrive_object(provider)

    try:
        drive.auth.service.files().trash(fileId=storage_key).execute()
        return True
    except:
        print('Delete failed: %s' % traceback.format_exc())
        return False


def get_children(drive, parent_id=None):
    children = []

    if parent_id is None or parent_id == 'root':
        query = "('root' in parents or sharedWithMe) and trashed=false"
    else:
        query = "'%s' in parents and trashed=false" % parent_id

    for f in drive.ListFile({'q': query}).GetList():
        children.append(f)

    return children


def get_children_from_filelist(files, parent_id=None):
    if parent_id is None or parent_id == 'root':
        def filter(f):
            if len(f['parents']) == 0:
                return True

            for parent in f['parents']:
                if parent['isRoot']:
                    return True

            return False

    else:
        def filter(f):
            for parent in f['parents']:
                if parent['id'] == parent_id:
                    return True

            return False

    return [f for f in files if filter(f)]


def get_all_files(drive):
    files = []

    query = 'trashed=false'

    for f in drive.ListFile({'q': query}).GetList():
        files.append(f)

    return files


def update_quota(provider, drive):
    try:
        quota = drive.auth.service.about().get().execute()['quotaBytesTotal']
    except:
        print('Could not get quota from Google Drive:')
        traceback.print_exc()
    else:
        provider.quota_bytes = quota
        provider.save()


def resync_from_gdrive(provider):
    drive = get_pydrive_object(provider)

    def update_or_create_file(file_data, parent_folder, child_files_map):
        if file_data['id'] in child_files_map.keys():
            file1 = child_files_map[file_data['id']]
            if file1.filename != file_data['title']:
                file1.name = file_data['title']
                file1.save()

            try:
                size = int(file_data['fileSize'])
                external_link = ''
            except (KeyError, ValueError):
                size = None
                try:
                    external_link = file_data['alternateLink']
                except:
                    print(file_data)
                    raise
            if file1.size != size or file1.external_link != external_link:
                file1.size = size
                file1.external_link = external_link
                file1.save()

            del(child_files_map[file_data['id']])
        else:
            # The file isn't present locally. Create it
            file1 = Datafile()
            file1.owner = provider.owner
            file1.folder = parent_folder
            file1.filename = file_data['title']
            file1.upload_state = DATAFILE_READY
            file1.storage_key = file_data['id']
            try:
                file1.size = int(file_data['fileSize'])
            except (KeyError, ValueError):
                file1.size = None
                file1.external_link = file_data['alternateLink']
            file1.save()

        return file1

    def update_or_create_folder(folder_data, parent_folder, child_folders_map):
        # Check that the folder is present on both sides
        if folder_data['id'] in child_folders_map.keys():
            folder = child_folders_map[folder_data['id']]
            if folder.name != folder_data['title']:
                folder.name = folder_data['title']
                folder.save()
            del(child_folders_map[folder_data['id']])
        else:
            # The folder isn't present locally. Create it
            folder = Folder()
            folder.owner = provider.owner
            folder.parent = parent_folder
            folder.name = folder_data['title']
            folder.storage_account = provider
            folder.storage_key = folder_data['id']
            folder.save()

        return folder

    def sync_folder_with_drive_2(all_files, local_folder):
        folder_id = local_folder.storage_key

        child_folders = list(Folder.objects.filter(parent=local_folder))
        child_folders_map = {}
        for child_folder in child_folders:
            child_folders_map[child_folder.storage_key] = child_folder

        child_files = list(Datafile.objects.filter(folder=local_folder))
        child_files_map = {}
        for child_file in child_files:
            child_files_map[child_file.storage_key] = child_file

        for c in get_children_from_filelist(all_files, parent_id=folder_id):
            if c['mimeType'] == FOLDER_MIMETYPE:
                folder = update_or_create_folder(c, local_folder, child_folders_map)
                sync_folder_with_drive_2(all_files, folder)
            else:
                update_or_create_file(c, local_folder, child_files_map)

        # Do we have any files on the local side that aren't on the distant side
        # anymore?
        for rem_folder_key in child_folders_map:
            rem_folder = child_folders_map[rem_folder_key]
            rem_folder.delete()

        for rem_file_key in child_files_map:
            rem_file = child_files_map[rem_file_key]
            rem_file.delete()

    def sync_folder_with_drive(local_folder):
        folder_id = local_folder.storage_key

        child_folders = list(Folder.objects.filter(parent=local_folder))
        child_folders_map = {}
        for child_folder in child_folders:
            child_folders_map[child_folder.storage_key] = child_folder

        child_files = list(Datafile.objects.filter(folder=local_folder))
        child_files_map = {}
        for child_file in child_files:
            child_files_map[child_file.storage_key] = child_file

        for c in get_children(drive, folder_id):
            if c['mimeType'] == FOLDER_MIMETYPE:
                folder = update_or_create_folder(c, local_folder, child_folders_map)
                sync_folder_with_drive(folder)

            else:
                update_or_create_file(c, local_folder, child_files_map)

        # Do we have any files on the local side that aren't on the distant side
        # anymore?
        for rem_folder_key in child_folders_map:
            rem_folder = child_folders_map[rem_folder_key]
            rem_folder.delete()

        for rem_file_key in child_files_map:
            rem_file = child_files_map[rem_file_key]
            rem_file.delete()

    all_files = get_all_files(drive)

    root_folder = Folder.objects.get(storage_account=provider, parent=None)
    sync_folder_with_drive_2(all_files, root_folder)

    #update_quota(provider, drive)
