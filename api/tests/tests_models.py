# coding: utf-8

# Copyright Luna Technology 2015

# DJANGO
from django.test import TestCase

# OUR WEBAPP
from ..factories import (
    B2DropProviderFactory,
    DatafileFactory,
    DatasetFactory,
    DatasetFileFactory,
    FolderFactory,
    GDriveProviderFactory,
    StorageAccountFactory,
    S3ProviderFactory,
    SyncOperationFactory,
    UserActionFactory,
    UserFactory,
)

from ..models import Folder, GDriveProvider, SyncOperation


class TestUserStorageAccount(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.storage_account = StorageAccountFactory.create()
        self.storage_account_real = S3ProviderFactory.create(owner=self.user)

    def test_display_name(self):
        assert self.storage_account.display_name == self.storage_account.name

        self.storage_account.name = ''
        self.storage_account.save()
        assert self.storage_account.display_name == self.storage_account.__unicode__()

        self.storage_account_real.name = ''
        self.storage_account_real.save()
        assert self.storage_account_real.display_name == self.storage_account_real.__unicode__()

    def test_utilization(self):
        assert self.storage_account.utilization == 0
        self.datafile = DatafileFactory.create(folder__storage_account=self.storage_account, size=5)
        assert self.storage_account.utilization == 5

    def test_quota(self):
        assert self.storage_account.quota is None
        assert self.storage_account_real.quota is None  # S3

        bdrop = B2DropProviderFactory.create(owner=self.user)
        assert bdrop.quota is None  # other provider

        gdrive = GDriveProviderFactory.create(owner=self.user)
        assert gdrive.quota is None  # gdrive with quota_bytes = 0

        gdrive.quota_bytes = 1
        gdrive.save()

        gdrive = GDriveProvider.objects.get(pk=gdrive.pk)
        assert gdrive.quota_bytes == gdrive.get_concrete().quota_bytes
        assert gdrive.quota == 1

    def test_get_root_folder(self):
        assert isinstance(self.storage_account.get_root_folder(), Folder)

    def test_unicode(self):
        assert 'StorageAccount' in self.storage_account.__unicode__()


class DatasetTest(TestCase):
    def setUp(self):
        self.dataset = DatasetFactory.create()

    def test_unicode(self):
        assert self.dataset.__unicode__() == self.dataset.name


class DatasetFileTest(TestCase):
    def setUp(self):
        self.dataset_file = DatasetFileFactory.create()

    def test_unicode(self):
        assert self.dataset_file.__unicode__() == self.dataset_file.datafile.filename


class FolderTest(TestCase):
    def setUp(self):
        self.folder = FolderFactory.create()
        self.folder_child = FolderFactory.create(parent=self.folder)
        self.folder_grand_child = FolderFactory.create(parent=self.folder_child)

    def test_rel_path(self):
        assert self.folder.rel_path == ''

        assert self.folder_child.rel_path == self.folder_child.name

        assert self.folder_grand_child.rel_path == "%s/%s" % (self.folder_child.rel_path, self.folder_grand_child.name)

    def test_unicode(self):
        assert self.folder.__unicode__() == self.folder.name


class DatafileTest(TestCase):
    def setUp(self):
        self.datafile = DatafileFactory.create()

    def test_unicode(self):
        assert self.datafile.__unicode__() == self.datafile.filename


class UserActionTest(TestCase):
    def setUp(self):
        self.user_action = UserActionFactory.create(
            args='{"dataset": "bliblablo"}',
            action_type='ACTION_TYPE_DOWNLOAD_DATASET')

    def test_text(self):
        assert self.user_action.text == self.user_action.__unicode__()

    def test_unicode(self):
        assert self.user_action.__unicode__() == 'An anonymous user downloaded dataset: bliblablo'


class SyncOperationTest(TestCase):
    def setUp(self):
        self.syncop = SyncOperationFactory.create()
        self.storage_account = StorageAccountFactory.create()

    def test_get_latest_for_account(self):
        assert self.syncop == SyncOperation.get_latest_for_account(self.syncop.storage_account)

        assert SyncOperation.get_latest_for_account(self.storage_account) is None
        assert SyncOperation.get_latest_for_account(None) is None

        assert SyncOperation.get_latest_for_account("foo") is None
