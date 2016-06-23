# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>

import os.path
import tempfile
import traceback

from ..data import DATAFILE_READY
from ..models import Datafile, Folder

from .packages import easywebdav


B2DROP_DOMAIN = '192.168.1.34'
B2DROP_PATH = 'webdav'


def _connect(foo):
    webdav = easywebdav.connect(
        B2DROP_DOMAIN,
        protocol='http',
        path=B2DROP_PATH,
        port=8080
    )

    return webdav


def check_webdav_credentials(provider):
    webdav = _connect(provider)
    webdav.ls('/')


def retrieve_file_from_webdav(datafile, provider):
    webdav = _connect(provider)

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfilename = tmpfile.name

            webdav.download(datafile.storage_key, tmpfilename)

            return tmpfilename

    except:
        print('Download failed: %s' % traceback.format_exc())
        return None


def create_folder_on_webdav(folder, provider):
    webdav = _connect(provider)

    remote_path = '/' + folder.rel_path + '/'
    webdav.mkdir(remote_path)

    return remote_path


def delete_file_from_webdav(provider, storage_key):
    webdav = _connect(provider)

    try:
        webdav.delete(storage_key)
        return True
    except:
        print('Delete failed: %s' % traceback.format_exc())
        return False


def split_relpath(relpath):
    while relpath.endswith('/'):
        relpath = relpath[:-1]

    folder, filename = os.path.split(relpath)

    return folder, filename


def resync_from_webdav(provider):
    webdav = _connect(provider)

    root_folder = provider.get_root_folder()

    child_folders = list(Folder.objects.filter(storage_account=provider).exclude(parent=None))
    child_folders_map = dict()
    for child_folder in child_folders:
        child_folders_map[child_folder.storage_key] = child_folder
    new_child_folders_map = dict()
    new_child_folders_map['/'] = root_folder

    child_files = list(Datafile.objects.filter(folder__storage_account=provider))
    child_files_map = {}
    for child_file in child_files:
        child_files_map[child_file.storage_key] = child_file

    # Fetch the data
    remote_data = webdav.ls('/')

    # Sort the elements of remote_data by increasing name length. This ensures that
    # a parent directory will be handled before its children
    remote_data.sort(key=lambda elt: len(elt.name))

    for f in remote_data:
        relpath = f.name[len(B2DROP_PATH) + 1:]

        if relpath == '/':
            # The root directory. Nothing to do
            continue

        parent_folder_path, filename = split_relpath(relpath)
        parent_folder = new_child_folders_map.get(parent_folder_path, None) or \
            new_child_folders_map.get(parent_folder_path + '/', None)

        if parent_folder is None:
            raise RuntimeError('Unknown parent folder: %s' % parent_folder_path)

        if f.contenttype == '':
            # It's a directory
            if relpath in child_folders_map.keys():
                folder = child_folders_map[relpath]
                del(child_folders_map[relpath])
            else:
                # The folder isn't present locally. Create it
                folder = Folder()
                folder.owner = provider.owner
                folder.parent = parent_folder
                folder.name = filename
                folder.storage_account = provider
                folder.storage_key = relpath
                folder.save()
            new_child_folders_map[relpath] = folder

        else:
            # It's a file
            if relpath in child_files_map.keys():
                file1 = child_files_map[relpath]

                size = int(f.size)
                if file1.size != size:
                    file1.size = size
                    file1.save()

                del(child_files_map[relpath])

            else:
                # The file isn't present locally. Create it
                file1 = Datafile()
                file1.owner = provider.owner
                file1.folder = parent_folder
                file1.filename = filename
                file1.upload_state = DATAFILE_READY
                file1.storage_key = relpath
                file1.size = f.size
                file1.save()

    for rem_folder_key in child_folders_map:
        rem_folder = child_folders_map[rem_folder_key]
        rem_folder.delete()

    for rem_file_key in child_files_map:
        rem_file = child_files_map[rem_file_key]
        rem_file.delete()


def upload_file_to_webdav(datafile, provider, tempfile_path):
    webdav = _connect(provider)

    remote_path = '/' + datafile.rel_path
    webdav.upload(tempfile_path, remote_path)

    return remote_path
