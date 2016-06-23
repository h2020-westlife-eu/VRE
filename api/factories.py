# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import factory

from django.contrib.auth.models import User

from .data import STORAGE_ACCOUNT_READY, STORAGE_ACCOUNT_PENDING_VALIDATION, DATAFILE_READY

from .models import (
    B2DropProvider,
    Datafile,
    Dataset,
    DatasetFile,
    DropboxProvider,
    DummyProvider,
    Folder,
    GDriveProvider,
    S3Provider,
    SyncOperation,
    UserAction,
    UserStorageAccount,
    WLWebdavProvider,
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: u"User %03d" % n)
    email = factory.LazyAttribute(lambda obj: u"%s@example.com" % obj.username)

    @classmethod
    def _generate(cls, create, attrs):
        """ Override the default _generate() to set the password """
        user = super(UserFactory, cls)._generate(create, attrs)
        user.set_password(u'password')
        user.save()
        return user


class S3ProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = S3Provider

    validation_state = STORAGE_ACCOUNT_READY


class GDriveProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GDriveProvider

    validation_state = STORAGE_ACCOUNT_READY


class UnvalidatedGDriveProviderFactory(GDriveProviderFactory):
    validation_state = STORAGE_ACCOUNT_PENDING_VALIDATION


class B2DropProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = B2DropProvider

    validation_state = STORAGE_ACCOUNT_READY


class WLWebdavProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WLWebdavProvider

    validation_state = STORAGE_ACCOUNT_READY


class DropboxProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DropboxProvider

    validation_state = STORAGE_ACCOUNT_READY


class UnvalidatedDropboxProviderFactory(DropboxProviderFactory):
    validation_state = STORAGE_ACCOUNT_PENDING_VALIDATION


class DummyProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DummyProvider

    validation_state = STORAGE_ACCOUNT_READY


class StorageAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserStorageAccount

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: u'StorageAccount %03d' % n)
    validation_state = STORAGE_ACCOUNT_READY


class UnvalidatedStorageAccountFactory(StorageAccountFactory):
    validation_state = STORAGE_ACCOUNT_PENDING_VALIDATION


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dataset

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: u'Dataset %03d' % n)


class FolderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Folder

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: u'Folder %03d' % n)
    storage_account = factory.SubFactory(
        StorageAccountFactory,
        owner=factory.SelfAttribute('..owner'),
    )


class DatafileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Datafile

    filename = factory.Sequence(lambda n: u'Datafile %03d' % n)
    owner = factory.SubFactory(UserFactory)
    folder = factory.SubFactory(FolderFactory, owner=factory.SelfAttribute('..owner'))


class UploadedDatafileFactory(DatafileFactory):
    upload_state = DATAFILE_READY
    storage_key = factory.Sequence(lambda n: u'ID%03d' % n)
    size = 444


class DatasetFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DatasetFile

    owner = factory.SubFactory(UserFactory)
    dataset = factory.SubFactory(
        DatasetFactory,
        owner=factory.SelfAttribute('..owner')
    )
    datafile = factory.SubFactory(
        DatafileFactory,
        owner=factory.SelfAttribute('..owner')
    )


class UnvalidatedFolderFactory(FolderFactory):
    storage_account = factory.SubFactory(
        UnvalidatedStorageAccountFactory,
        owner=factory.SelfAttribute('..owner'),
    )


class UserActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserAction

    user = factory.SubFactory(UserFactory)


class SyncOperationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SyncOperation

    storage_account = factory.SubFactory(StorageAccountFactory)
