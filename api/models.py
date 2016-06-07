import copy
import json

from django.contrib.auth.models import User
from django.core import signing
from django.db import models

from .jobportals.portals import PORTAL_FORMS

from .data import (
    DATAFILE_STATES,
    DATAFILE_STATE_CHOICES,
    DATAFILE_TRANSFER_IN_PROGRESS,
    EXTERNAL_SUBMISSION_STATE_CHOICES,
    EXTERNAL_SUBMISSION_PENDING_SUBMISSION,
    ACTIONS_TEXT,
    STORAGE_ACCOUNT_PENDING_VALIDATION,
    STORAGE_ACCOUNT_READY,
    STORAGE_ACCOUNT_STATES,
    STORAGE_ACCOUNT_STATE_CHOICES,
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserStorageAccount(BaseModel):
    root_folder_key = ''

    owner = models.ForeignKey(User)

    name = models.CharField(max_length=255, blank=True)

    validation_state = models.CharField(max_length=255, choices=STORAGE_ACCOUNT_STATE_CHOICES,
                                        default=STORAGE_ACCOUNT_PENDING_VALIDATION)

    _concrete = None

    def get_concrete(self):
        """
        :return: the concrete instance of this storage account
        """
        for attr in ['s3provider', 'gdriveprovider', 'b2dropprovider', 'dropboxprovider', 'dummyprovider']:
            try:
                inst = getattr(self, attr)
                return inst
            except:
                pass
        return None

    @property
    def display_name(self):
        if self.name != '':
            return self.name
        else:
            if self.get_concrete() is not None:
                return self.get_concrete().__unicode__()
            else:
                return self.__unicode__()

    @property
    def utilization(self):
        s = Datafile.objects.filter(folder__storage_account=self).aggregate(models.Sum('size'))['size__sum']
        if s is None:
            return 0
        else:
            return s

    @property
    def readable_validation_state(self):
        return STORAGE_ACCOUNT_STATES.get(self.validation_state, 'Unknown')

    @property
    def validated(self):
        return self.validation_state == STORAGE_ACCOUNT_READY

    @property
    def quota(self):
        inst = self.get_concrete()
        if inst is None:
            return None
        elif inst.type == 'GDRIVE_PROVIDER':
            if inst.quota_bytes == 0:
                return None
            else:
                return inst.quota_bytes
        else:
            return None

    @property
    def sync_in_progress(self):
        sync_op = SyncOperation.get_latest_for_account(self)
        if sync_op is None:
            return False
        else:
            return sync_op.ongoing

    def get_root_folder(self):
        return Folder.objects.get(storage_account=self, parent=None)

    def __unicode__(self):
        return u'StorageAccount%d' % self.pk


class S3Provider(UserStorageAccount):
    type = 'S3_PROVIDER'

    root_folder_key = '/'

    access_key_id = models.CharField(max_length=255)
    secret_access_key = models.CharField(max_length=255)
    bucket_name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'S3Provider (bucket: %s, access_key: %s)' % (self.bucket_name, self.access_key_id)


class GDriveProvider(UserStorageAccount):
    type = 'GDRIVE_PROVIDER'
    root_folder_key = 'root'

    credentials = models.CharField(max_length=4096)
    quota_bytes = models.BigIntegerField(default=0)

    def __unicode__(self):
        return u'GDriveProvider'


class B2DropProvider(UserStorageAccount):
    type = 'B2DROP_PROVIDER'
    root_folder_key = '/'

    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __unicode__(self):
        return u'B2DropProvider'


class DropboxProvider(UserStorageAccount):
    type = 'DROPBOX'
    root_folder_key = '/'

    access_user_id = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    quota_bytes = models.BigIntegerField(default=0)

    def __unicode__(self):
        return u'DropboxProvider'


class DummyProvider(UserStorageAccount):
    type = 'DUMMY'
    root_folder_key = '/'

    def __unicode__(self):
        return u'DummyProvider'


class Dataset(BaseModel):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=1024)

    published = models.BooleanField(default=False)
    publish_key = models.CharField(max_length=1024, default='')

    def publish(self, expires=None):
        self.published = True
        self.publish_key = signing.dumps({'pk': self.pk})
        self.save()

    def unpublish(self):
        self.published = False
        self.publish_key = ''
        self.save()

    def __unicode__(self):
        return self.name


class DatasetFile(BaseModel):
    owner = models.ForeignKey(User)
    dataset = models.ForeignKey(Dataset)

    datafile = models.ForeignKey('Datafile')

    def __unicode__(self):
        return self.datafile.filename

    class Meta:
        unique_together = ('dataset', 'datafile')


class Folder(BaseModel):
    owner = models.ForeignKey(User)
    parent = models.ForeignKey('Folder', null=True)
    name = models.CharField(max_length=1024)

    storage_account = models.ForeignKey(UserStorageAccount)
    storage_key = models.CharField(max_length=1024)

    @property
    def full_path(self):
        # TODO: Optimize this. MPTT?
        if self.parent is None:
            return self.name
        else:
            return self.parent.full_path + '/' + self.name

    @property
    def rel_path(self):
        """
        :return: the path relative to the provider root
        """
        # TODO: What if there is a '/' in the path??
        # TODO: Optimize this. MPTT?
        if self.parent is None:
            return ''
        elif self.parent.parent is None:
            return self.name
        else:
            return self.parent.rel_path + '/' + self.name

    def __unicode__(self):
        return self.name


class Datafile(BaseModel):
    filename = models.CharField(max_length=1024)

    owner = models.ForeignKey(User)
    folder = models.ForeignKey(Folder)

    upload_state = models.CharField(
        max_length=255, choices=DATAFILE_STATE_CHOICES, default=DATAFILE_TRANSFER_IN_PROGRESS)

    # storage_account = models.ForeignKey(UserStorageAccount)
    storage_key = models.CharField(max_length=1024)

    size = models.IntegerField(null=True, default=None)
    external_link = models.URLField(max_length=8192, blank=True)

    @property
    def storage_account(self):
        return self.folder.storage_account

    @property
    def full_path(self):
        return self.folder.full_path + '/' + self.filename

    @property
    def rel_path(self):
        return self.folder.rel_path + '/' + self.filename

    @property
    def readable_upload_state(self):
        return DATAFILE_STATES.get(self.upload_state, 'Unknown')

    def __unicode__(self):
        return self.filename


class UserAction(BaseModel):
    user = models.ForeignKey(User)
    action_type = models.CharField(max_length=255)
    args = models.TextField()

    @property
    def text(self):
        return self.__unicode__()

    @classmethod
    def log(cls, user, action_type, args):
        # TODO: validate that args match action_type?
        obj = cls(user=user, action_type=action_type, args=json.dumps(args))
        obj.save()
        return obj

    def __unicode__(self):
        try:
            args = json.loads(self.args)
        except ValueError:
            args = {}
        args.update({'user': self.user.username})

        r = ACTIONS_TEXT[self.action_type] % args
        return r

    class Meta:
        ordering = ['-created_at']


class SyncOperation(BaseModel):
    storage_account = models.ForeignKey(UserStorageAccount)
    ongoing = models.BooleanField(default=False)

    @classmethod
    def get_latest_for_account(cls, storage_account):
        """
        Returns the most recent SyncOperation for a given UserStorageAccount
        :param storage_account:
        :return: the latest SyncOperation, or None if there hasn't been any
        """
        try:
            obj = cls.objects.filter(storage_account=storage_account).order_by('-created_at')[0]
        except:
            obj = None
        return obj


class ExternalCredentials(BaseModel):
    provider_name = models.CharField(max_length=1024)
    owner = models.ForeignKey(User)
    username = models.CharField(max_length=1024)
    password = models.CharField(max_length=1024)

    def __unicode__(self):
        return 'ExternalCredentials(%s, %s)' % (self.provider_name, self.username)


class ExternalJobPortal(BaseModel):
    name = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name


class ExternalJobPortalFormGroup(BaseModel):
    portal = models.ForeignKey(ExternalJobPortal)
    parent = models.ForeignKey('ExternalJobPortalFormGroup', null=True)
    name = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name


class ExternalJobPortalForm(BaseModel):
    portal = models.ForeignKey(ExternalJobPortal)
    parent = models.ForeignKey(ExternalJobPortalFormGroup, null=True)
    name = models.CharField(max_length=1024)

    original_url = models.URLField()
    submit_url = models.URLField()

    template_name = models.CharField(max_length=1024)

    @classmethod
    def load_initial(cls):
        portal_forms = copy.deepcopy(PORTAL_FORMS)
        for portal_form in portal_forms:
            # Save the portal
            portal, created = ExternalJobPortal.objects.update_or_create(pk=portal_form['portal']['pk'], defaults=portal_form['portal'])
            if created:
                print('Created portal %d' % portal.pk)
            portal_form['portal'] = portal

            new_portal_form, created = cls.objects.update_or_create(pk=portal_form['pk'], defaults=portal_form)
            if created:
                print('Created portal_form %d' % new_portal_form.pk)
            new_portal_form.save()

    def __unicode__(self):
        return self.name


class ExternalJobPortalSubmission(BaseModel):
    owner = models.ForeignKey(User)
    target = models.ForeignKey(ExternalJobPortalForm)
    data = models.TextField()

    job_key = models.CharField(max_length=1024, blank=True)

    @property
    def state(self):
        try:
            states = ExternalJobPortalSubmissionStateChange.objects.filter(external_submission=self)
            states = states.order_by('-created_at')
            state = states[0]
        except:
            state = EXTERNAL_SUBMISSION_PENDING_SUBMISSION
        return state

    def update_state(self, new_state):
        state_change = ExternalJobPortalSubmissionStateChange(external_submission=self, state=new_state)
        state_change.save()

    def __unicode__(self):
        return 'ExternalSubmission(%d)' % self.pk


class ExternalJobPortalSubmissionStateChange(BaseModel):
    external_submission = models.ForeignKey(ExternalJobPortalSubmission)
    state = models.CharField(max_length=256, choices=EXTERNAL_SUBMISSION_STATE_CHOICES)
