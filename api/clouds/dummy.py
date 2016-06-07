# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>

"""
This defines a dummy provider.
It is not meant to be exposed to the end-user, but rather to be used in tests, etc.
It stores folder hierarchy and data in redis
"""

import base64
import json
import tempfile
import traceback

from django.conf import settings

from redis import StrictRedis


def _connect(provider):
    r = StrictRedis()
    return r


def _get_key_for_file(path):
    return settings.DEPLOYMENT_BASENAME + '.dummy_provider.' + base64.b64encode(path)


def check_credentials(provider):
    """
    Makes a minimal call to the remote API, to check that the credentials that we have are
    functional
    :param provider:
    :return:
    """
    r = _connect(provider)
    r.keys(settings.DEPLOYMENT_BASENAME + '.dummy_provider.*')


def retrieve(datafile, provider):
    """
    Retrieve a file from the remote provider
    :param datafile:
    :param provider:
    :return: the path to a temporary file containing the data, or None
    """
    r = _connect(provider)

    try:
        data = base64.b64decode(json.loads(r.get(datafile.storage_key))['data'])
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile.write(data)
            tmpfilename = tmpfile.name

        return tmpfilename
    except:
        print('Download failed: %s' % traceback.format_exc())
        return None


def create_folder(folder, provider):
    """
    Create a folder on the remote provider
    :param folder:
    :param provider:
    :return: the storage_key of the created folder on the remote provider
    """
    r = _connect(provider)

    storage_key = _get_key_for_file(folder.rel_path)
    r.set(storage_key, json.dumps({'is_folder': True}))

    return storage_key


def delete(provider, storage_key):
    """
    Delete a file on the remote provider
    :param provider:
    :param storage_key:
    :return: True on success, False on failure
    """
    r = _connect(provider)

    r.delete(storage_key)
    return True


def resync(provider):
    """
    Synchronise the folder hierarchy data from the remote provider to the local cache
    :param provider:
    :return:
    """
    pass


def upload(datafile, provider, tempfile_path):
    """
    Upload a file into the remote provider
    :param datafile:
    :param provider:
    :param tempfile_path: the path of a temporary file containing the data to upload
    :return: the storage_key of the created file on the remote provider
    """
    r = _connect(provider)

    with open(tempfile_path, 'rb') as fh:
        data = fh.read()

    storage_key = _get_key_for_file(datafile.rel_path)
    r.set(storage_key, json.dumps({'data': base64.b64encode(data)}))

    return storage_key