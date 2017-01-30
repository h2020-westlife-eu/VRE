# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from django.core import signing

from rest_framework import serializers
from rest_framework.compat import unicode_to_repr
from rest_framework.utils.representation import smart_repr

from .data import DATAFILE_READY

from .models import (
    B2DropProvider,
    Datafile,
    Dataset,
    DatasetFile,
    DropboxProvider,
    ExternalJobPortal,
    ExternalJobPortalForm,
    ExternalJobPortalSubmission,
    Folder,
    GDriveProvider,
    S3Provider,
    UserAction,
    UserStorageAccount,
    WLWebdavProvider
)


class UniqueForUserValidator(object):
    """
    Heavily inspired from rest_framework.validators.BaseUniqueForValidator,
    which does the same thing, but with a date instead of an user
    """
    message = 'This field must be unique for the current user'
    missing_message = 'This field is required.'

    def __init__(self, queryset, field, user_field="owner", message=None):
        self.queryset = queryset
        self.field = field
        self.user_field = user_field
        self.message = message or self.message

    def set_context(self, serializer):
        # Determine the underlying model field names. These may not be the
        # same as the serializer field names if `source=<>` is set.
        self.field_name = serializer.fields[self.field].source_attrs[0]
        self.owner_field_name = self.user_field

        # Determine the existing instance, if this is an update operation
        self.instance = getattr(serializer, 'instance', None)

        # Determine the current user, which will be set as owner of the object
        # This implies a number of assumptions:
        # - there is a logged-in user
        # - this user will be set as owner of the object
        # - The serializer is called from a viewset, which has ViewsetInjectRequestMixin
        #     (or something equivalent)
        self.owner = serializer.context.get('request').user

    def enforce_required_fields(self, attrs):
        """
        The `UniqueForUserValidator` class always forces an implied
        'required' state on the fields it is applied to.
        """
        if self.field not in attrs:
            missing = {
                self.field: self.missing_message
            }
            raise serializers.ValidationError(missing)

    def filter_queryset(self, attrs, queryset):
        value = attrs[self.field]
        user = self.owner

        filter_kwargs = {}
        filter_kwargs[self.field_name] = value
        filter_kwargs[self.owner_field_name] = user

        return queryset.filter(**filter_kwargs)

    def exclude_current_instance(self, attrs, queryset):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict
        """
        if self.instance is not None:
            return queryset.exclude(pk=self.instance.pk)
        return queryset

    def __call__(self, attrs):
        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset)
        queryset = self.exclude_current_instance(attrs, queryset)
        if queryset.exists():
            raise serializers.ValidationError({self.field: self.message})

    def __repr__(self):
        return unicode_to_repr('<%s(queryset=%s, field=%s)>' % (
            self.__class__.__name__,
            smart_repr(self.queryset),
            smart_repr(self.field)
        ))


class DatasetSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()
    modified_at = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField(source='owner.pk')

    class Meta:
        model = Dataset
        fields = ('pk', 'created_at', 'modified_at', 'owner', 'name', 'published', 'publish_key')
        extra_kwargs = {
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'owner': {'read_only': True},
            'published': {'read_only': True},
            'publish_key': {'read_only': True},
        }


class DatasetFileSerializer(serializers.ModelSerializer):
    source_path = serializers.ReadOnlyField(source='datafile.full_path')
    size = serializers.ReadOnlyField(source='datafile.size')

    class Meta:
        model = DatasetFile
        fields = ('pk', 'created_at', 'modified_at', 'owner', 'dataset', 'datafile', 'source_path', 'size')
        extra_kwargs = {
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'owner': {'read_only': True},
        }

    def validate_dataset(self, value):
        cur_user = self.context.get('request').user

        if value is None:
            raise serializers.ValidationError('You must specify a dataset')

        if value.owner != cur_user:
            raise serializers.ValidationError("You don't have the rights to add a file to this dataset")

        if value.published is True:
            raise serializers.ValidationError("Cannot add a file to a published dataset")

        return value

    def validate_datafile(self, value):
        cur_user = self.context.get('request').user

        if value is None:
            raise serializers.ValidationError('You must specify a datafile')

        if value.owner != cur_user:
            raise serializers.ValidationError("You don't have the rights to add this file to a dataset")

        if value.upload_state != DATAFILE_READY:
            raise serializers.ValidationError('This datafile is still being uploaded')

        if value.size is None:
            raise serializers.ValidationError('Adding virtual files to a dataset is not currently supported')

        return value


class FolderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = (
            'pk', 'created_at', 'modified_at', 'name', 'parent', 'owner', 'storage_account',
        )
        extra_kwargs = {
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'storage_account': {'read_only': True},
            'owner': {'read_only': True}
        }

    def validate_parent(self, value):
        cur_user = self.context.get('request').user

        if value is None:
            raise serializers.ValidationError("Cannot create a folder without a parent folder.")

        if value.owner != cur_user:
            raise serializers.ValidationError("You don't have the rights to add a subfolder to this folder.")

        if value.storage_account.validated is False:
            raise serializers.ValidationError("This storage account is not ready yet.")

        return value


class DatafileSerializer(serializers.ModelSerializer):
    storage_account_name = serializers.ReadOnlyField(source='storage_account.display_name')
    download_key = serializers.SerializerMethodField()

    class Meta:
        model = Datafile
        fields = (
            'pk', 'created_at', 'modified_at', 'filename', 'owner', 'folder', 'size',
            'readable_upload_state', 'storage_account_name', 'external_link', 'download_key',
        )
        extra_kwargs = {
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
            'size': {'read_only': True},
            'readable_upload_state': {'read_only': True},
            'owner': {'read_only': True},
            'external_link': {'read_only': True},
            'download_key': {'read_only': True},
        }

    def get_download_key(self, obj):
        return signing.dumps({
            'pk': obj.pk,
            'user': self.context['request'].user.pk,
        })

    def validate_folder(self, value):
        cur_user = self.context.get('request').user

        if value.owner != cur_user:
            raise serializers.ValidationError("You don't have the rights to add a file to this folder.")

        if value.storage_account.validated is False:
            raise serializers.ValidationError("This storage account is not ready yet.")

        return value


class UserStorageAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStorageAccount
        fields = ('pk', 'owner', 'name', 'quota', 'utilization', 'validated', 'display_name',
                  'readable_validation_state', 'sync_in_progress')


class S3ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3Provider
        fields = ('pk', 'name', 'access_key_id', 'secret_access_key', 'bucket_name',)
        extra_kwargs = {
            'secret_access_key': {'write_only': True}
        }
        validators = [
            UniqueForUserValidator(
                queryset=S3Provider.objects.all(),
                field='access_key_id',
                message='You have already linked this account'
            )
        ]


class GDriveProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GDriveProvider
        fields = ('pk', 'name',)


class DropboxProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropboxProvider
        fields = ('pk', 'name', )


class B2DropProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2DropProvider
        fields = ('pk', 'name', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }
        validators = [
            UniqueForUserValidator(
                queryset=B2DropProvider.objects.all(),
                field='username',
                message='You have already linked this account'
            )
        ]


class WLWebdavProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WLWebdavProvider
        fields = ('pk', 'name')
        # extra_kwargs = {
        #     'password': {'write_only': True}
        # }
        # validators = [
        #     UniqueForUserValidator(
        #         queryset=B2DropProvider.objects.all(),
        #         field='username',
        #         message='You have already linked this account'
        #     )
        # ]


class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ('pk', 'created_at', 'text')
        extra_kwargs = {
            'created_at': {'read_only': True},
            'text': {'read_only': True},
        }


class ExternalJobPortalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalJobPortal
        fields = ('pk', 'name')
        extra_kwargs = {
            'name': {'read_only': True},
        }


class ExternalJobPortalFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalJobPortalForm
        fields = ('pk', 'name', 'portal', 'parent', 'template_name')
        extra_kwargs = {
            'name': {'read_only': True},
            'portal': {'read_only': True},
            'parent': {'read_only': True},
            'template_name': {'read_only': True},
        }


class ExternalJobPortalSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalJobPortalSubmission
        fields = ('pk', 'created_at', 'target', 'data', 'state')
        extra_kwargs = {
            'created_at': {'read_only': True},
            'state': {'read_only': True},
        }

from django.contrib.auth.models import User
# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')