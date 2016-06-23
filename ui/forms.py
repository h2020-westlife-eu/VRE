# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from django import forms
from django.db.models.query import EmptyQuerySet
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm as PwdChangeForm

from api.models import Dataset, Datafile, Folder, S3Provider, GDriveProvider, B2DropProvider, DropboxProvider, WLWebdavProvider

from .mixins import AngularModelFormMixin, AngularFormMixin


class EmptyQuerysetsMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmptyQuerysetsMixin, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if isinstance(self.fields[field_name], forms.ModelChoiceField):
                self.fields[field_name].queryset = self.Meta.model.objects.none()


class LoginForm(AngularFormMixin, AuthenticationForm):
    scope_prefix = 'dj_login'
    form_name = 'login_form'


class ForgotPasswordForm(AngularFormMixin, PasswordResetForm):
    scope_prefix = 'dj_forgot_password'
    form_name = 'forgot_password_form'


class ResetPasswordForm(AngularFormMixin):
    scope_prefix = 'dj_reset_password'
    form_name = 'reset_password_form'

    new_password = forms.CharField(label="Password",
                                   widget=forms.PasswordInput)
    re_new_password = forms.CharField(label="Password confirmation",
                                      widget=forms.PasswordInput,
                                      help_text="Enter the same password as before, for verification.")


class RegisterForm(AngularModelFormMixin):
    scope_prefix = 'dj_register'
    form_name = 'register_form'

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')
        widgets = {'password': forms.PasswordInput()}

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True


class PasswordChangeForm(AngularFormMixin, PwdChangeForm):
    scope_prefix = 'dj_change_password'
    form_name = 'change_password_form'


class DatasetForm(AngularModelFormMixin):
    scope_prefix = 'dj_dataset'
    form_name = 'dataset_form'

    class Meta:
        model = Dataset
        fields = ('name', )


class DatafileForm(AngularModelFormMixin):
    scope_prefix = 'dj_datafile'
    form_name = 'datafile_form'

    class Meta:
        model = Datafile
        fields = ('filename',)
        widgets = {'filename': forms.HiddenInput()}


class DatafileUpdateForm(AngularModelFormMixin):
    scope_prefix = 'dj_datafile_update'
    form_name = 'datafile_update_form'

    class Meta:
        model = Datafile
        fields = ('filename',)


class FolderForm(AngularModelFormMixin):
    scope_prefix = 'dj_folder'
    form_name = 'folder_form'

    class Meta:
        model = Folder
        fields = ('name',)


class S3ProviderForm(AngularModelFormMixin):
    scope_prefix = 'dj_s3provider'
    form_name = 's3provider_form'

    class Meta:
        model = S3Provider
        fields = ('name', 'access_key_id', 'secret_access_key', 'bucket_name', )


class GDriveProviderForm(AngularModelFormMixin):
    scope_prefix = 'dj_gdriveprovider'
    form_name = 'gdriveprovider_form'

    class Meta:
        model = GDriveProvider
        fields = ('name', )


class DropboxProviderForm(AngularModelFormMixin):
    scope_prefix = 'dj_dropboxprovider'
    form_name = 'dropboxprovider_form'

    class Meta:
        model = DropboxProvider
        fields = ('name', )


class B2DropProviderForm(AngularModelFormMixin):
    scope_prefix = 'dj_b2dropprovider'
    form_name = 'b2dropprovider_form'

    class Meta:
        model = B2DropProvider
        fields = ('name', 'username', 'password',)


class WLWebdavProviderForm(AngularModelFormMixin):
    scope_prefix = 'dj_wlwebdavprovider'
    form_name = 'wlwebdavprovider_form'

    class Meta:
        model = WLWebdavProvider
        fields = ('name', )


class DatasetAddFileForm(AngularFormMixin):
    scope_prefix = 'dj_dataset_add_file'
    form_name = 'dataset_add_file_form'

    selected_datafile = forms.HiddenInput()
