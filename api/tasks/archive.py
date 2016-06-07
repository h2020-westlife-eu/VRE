# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import os.path
import tarfile
from tempfile import NamedTemporaryFile

from api.models import DatasetFile

from .storage import retrieve_file


def create_archive_from_dataset(dataset):
    datasetfiles = DatasetFile.objects.filter(dataset=dataset).select_related('datafile')

    temporary_fd = NamedTemporaryFile()

    with tarfile.open(fileobj=temporary_fd, mode='w|gz') as tf:

        for datasetfile in datasetfiles:
            datafile = datasetfile.datafile
            datafile_basename = os.path.split(datafile.filename)[1]

            tmpfilename = retrieve_file(datafile.pk)
            with open(tmpfilename, 'rb') as tmpfile:

                ti = tarfile.TarInfo(datafile_basename)
                ti.size = datafile.size
                tf.addfile(ti, tmpfile)

    temporary_fd.seek(0)

    return temporary_fd
