import os
import tempfile
import traceback

import sys
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core import signing
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions
from rest_framework.decorators import detail_route, list_route
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .clouds import gdrive
from .clouds import dbox

from .data import (
    ACTION_TYPE_UPLOAD,
    ACTION_TYPE_DOWNLOAD,
    ACTION_TYPE_CREATE_FOLDER,
    ACTION_TYPE_DELETE_FILE,
    ACTION_TYPE_CREATE_DATASET,
    ACTION_TYPE_DELETE_DATASET,
    ACTION_TYPE_PUBLISH_DATASET,
    ACTION_TYPE_UNPUBLISH_DATASET,
    ACTION_TYPE_DOWNLOAD_DATASET,
    ACTION_TYPE_JOBPORTAL_SUBMIT,
)

from .models import (
    B2DropProvider,
    Dataset,
    DatasetFile,
    Datafile,
    DropboxProvider,
    ExternalJobPortal,
    ExternalJobPortalForm,
    ExternalJobPortalSubmission,
    Folder,
    GDriveProvider,
    UserAction,
    UserStorageAccount,
    S3Provider,
    WLWebdavProvider
)
from .permissions import IsOwner
from .serializers import (
    B2DropProviderSerializer,
    DatasetSerializer,
    DatasetFileSerializer,
    DatafileSerializer,
    DropboxProviderSerializer,
    ExternalJobPortalSerializer,
    ExternalJobPortalFormSerializer,
    ExternalJobPortalSubmissionSerializer,
    FolderSerializer,
    GDriveProviderSerializer,
    UserActionSerializer,
    UserStorageAccountSerializer,
    S3ProviderSerializer,
    WLWebdavProviderSerializer
)

from .tasks import check_credentials, upload_file, delete_file, retrieve_file, resync
from .tasks.archive import create_archive_from_dataset


class ViewsetInjectRequestMixin(object):
    """
    Injects self.request in the context of the serializer
    """
    def get_serializer_context(self):
        return {'request': self.request}


class DatasetViewSet(ViewsetInjectRequestMixin, viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return Dataset.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        dataset = serializer.save(owner=self.request.user)
        UserAction.log(self.request.user, ACTION_TYPE_CREATE_DATASET, {'dataset': dataset.name})

    def perform_destroy(self, instance):
        UserAction.log(self.request.user, ACTION_TYPE_DELETE_DATASET, {'dataset': instance.name})
        super(DatasetViewSet, self).perform_destroy(instance)

    @detail_route(methods=['POST'])
    def publish(self, request, pk):
        dataset = self.get_object()
        foo = self.request.POST

        if dataset.published is True:
            raise ValidationError('Dataset is already published')

        dataset.publish()
        UserAction.log(self.request.user, ACTION_TYPE_PUBLISH_DATASET, {'dataset': dataset.name})

        serializer = self.get_serializer(dataset)
        return Response(serializer.data)

    @detail_route(methods=['POST'])
    def unpublish(self, request, pk):
        dataset = self.get_object()
        foo = self.request.POST

        if dataset.published is False:
            raise ValidationError('Dataset is not published')

        dataset.unpublish()
        UserAction.log(self.request.user, ACTION_TYPE_UNPUBLISH_DATASET, {'dataset': dataset.name})

        serializer = self.get_serializer(dataset)
        return Response(serializer.data)

    @list_route(methods=['GET'], permission_classes=(), renderer_classes=(JSONRenderer,))
    def download(self, request, **kwargs):
        try:
            state = signing.loads(request.GET['publish_key'])
            pk = state['pk']
        except (KeyError, signing.BadSignature):
            traceback.print_exc()
            raise ValidationError('Corrupted or missing state')

        dataset = get_object_or_404(Dataset, pk=pk, published=True)

        try:
            archive_fd = create_archive_from_dataset(dataset)

            response = FileResponse(archive_fd, content_type='application/x-tar')
            response['Content-Disposition'] = 'attachment; filename="%s"' % "pype_archive.tgz"

            UserAction.log(dataset.owner, ACTION_TYPE_DOWNLOAD_DATASET, {'dataset': dataset.name})

            return response

        except:
            traceback.print_exc()
            return Response({})


class DatasetFileViewSet(ViewsetInjectRequestMixin, viewsets.ModelViewSet):
    serializer_class = DatasetFileSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return DatasetFile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DatafileViewSet(ViewsetInjectRequestMixin, viewsets.ModelViewSet):
    serializer_class = DatafileSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return Datafile.objects.filter(owner=self.request.user).order_by('filename')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        provider_pk = instance.storage_account.pk
        storage_key = instance.storage_key

        # If the file corresponds to a real file on a backend, schedule it for deletion
        if storage_key != u'':
            delete_file.delay(provider_pk, storage_key)

        UserAction.log(self.request.user, ACTION_TYPE_DELETE_FILE, {'path': instance.full_path})

        super(DatafileViewSet, self).perform_destroy(instance)

    @detail_route(methods=['POST'])
    def upload(self, request, pk):
        datafile = self.get_object()

        f = request.FILES['file']
        total_length = 0
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            for chunk in f.chunks():
                tmpfile.write(chunk)
                total_length += len(chunk)

            tmpfilename = tmpfile.name

        print("Uploaded length:", total_length)

        upload_file(pk, tmpfilename)

        print("Backend upload done")
        UserAction.log(self.request.user, ACTION_TYPE_UPLOAD, {'path': datafile.full_path})

        return Response({})

    @detail_route(methods=['GET'], permission_classes=(), renderer_classes=(JSONRenderer,))
    def download(self, request, pk, **kwargs):
        pk = int(pk)

        try:
            state = signing.loads(request.GET['download_key'])
            check_pk = state['pk']
            user_id = state['user']
        except (KeyError, signing.BadSignature):
            traceback.print_exc()
            raise ValidationError('Corrupted or missing state')

        if check_pk != pk:
            print('Download_key check failure: %s != %s' % (pk, check_pk))
            raise ValidationError('Invalid download_key')

        try:
            user = User.objects.get(pk=user_id)
        except:
            traceback.print_exc()
            raise ValidationError('Corrupted or missing state')

        datafile = get_object_or_404(Datafile, pk=pk)
        datafile_basename = os.path.split(datafile.filename)[1]

        try:
            tmpfilename = retrieve_file(pk)

            response = FileResponse(open(tmpfilename, 'rb'), content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="%s"' % datafile_basename

            # We *can* delete the file right now, it won't affect the already opened copy that we passed to
            # FileResponse(). This assumes that we're running on linux.
            os.remove(tmpfilename)

            UserAction.log(user, ACTION_TYPE_DOWNLOAD, {'path': datafile.full_path})

        except:
            traceback.print_exc()
            response = Response({})

        return response


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return Folder.objects.filter(owner=self.request.user).order_by('name')

    def perform_create(self, serializer):
        v = serializer.save(owner=self.request.user, storage_account=serializer.validated_data['parent'].storage_account)
        UserAction.log(self.request.user, ACTION_TYPE_CREATE_FOLDER, {'path': v.full_path})


class UserStorageAccountViewSet(ViewsetInjectRequestMixin, DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = UserStorageAccountSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return UserStorageAccount.objects.filter(owner=self.request.user)

    @detail_route(methods=['POST'])
    def resync(self, request, *args, **kwargs):
        foo = self.request.POST
        resync(self.get_object().pk)
        return self.retrieve(request, *args, **kwargs)


class ProviderCreateMixin(object):
    def perform_create(self, serializer):
        s = serializer.save(owner=self.request.user)
        provider_pk = s.userstorageaccount_ptr_id
        (check_credentials.si(provider_pk) | (resync.si(provider_pk)))()


class S3ProviderViewSet(ViewsetInjectRequestMixin, ProviderCreateMixin, CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = S3ProviderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)


class GDriveProviderViewSet(ViewsetInjectRequestMixin, CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = GDriveProviderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return GDriveProvider.objects.filter(owner=self.request.user)

    # This is the OAuth callback endpoint. It is registered in our GDrive app configuration, so
    # that users are redirected here after having granted rights to our app on the google website
    #
    # permission_classes is set to empty on this, but we require a signed 'state'
    # value, so it should be okay
    @list_route(methods=['GET'], permission_classes=(), renderer_classes=(JSONRenderer,))
    def confirm_link(self, request, **kwargs):
        try:
            state = signing.loads(request.GET['state'])
            pk = state['pk']
        except (KeyError, signing.BadSignature):
            raise ValidationError('Corrupted or missing state')

        try:
            code = request.GET['code']
        except KeyError:
            raise ValidationError('Bad or missing code')

        try:
            # We can't use self.get_queryset() here because are in an anonymous request, so self.request.user is
            # not defined
            gdrive_provider = GDriveProvider.objects.get(pk=pk)
        except:
            raise ValidationError('Corrupted or missing state')

        try:
            credentials_json = gdrive.step2_redeem_code_for_credentials(code)
        except:
            raise ValidationError('Invalid code')

        gdrive_provider.credentials = credentials_json
        gdrive_provider.save()

        provider_pk = gdrive_provider.userstorageaccount_ptr_id
        (check_credentials.si(provider_pk) | resync.si(provider_pk))()

        return HttpResponseRedirect('/home/#/storage_providers')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @detail_route()
    def get_redirect_to_accept_page(self, request, pk):
        """
        Get a redirection URL to Google OAuth authentication page
        :param request:
        :param pk:
        :return:
        """
        gdrive_provider = self.get_object()
        state = signing.dumps({'pk': gdrive_provider.pk})

        return Response({
            'url': gdrive.step1_get_authorize_url(state=state)
        })


class DropboxProviderViewSet(ViewsetInjectRequestMixin, CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = DropboxProviderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return DropboxProvider.objects.filter(owner=self.request.user)

    # This is the OAuth callback endpoint. It is registered in our GDrive app configuration, so
    # that users are redirected here after having granted rights to our app on the google website
    #
    # permission_classes is set to empty on this, but we require a signed 'state'
    # value, so it should be okay
    @list_route(methods=['GET'], permission_classes=(), renderer_classes=(JSONRenderer, ))
    def confirm_link(self, request, **kwargs):
        '''
        After oauth2, we retrieve and save access_token and user_id
        '''

        try:
            _state = request.GET['state'].split('|')
        except KeyError as e:
            raise e

        try:
            state_encoded = _state[1]
            state = signing.loads(state_encoded)
            pk = state['pk']
            user_pk = state['user_pk']
            user = User.objects.get(pk=user_pk)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
        except KeyError, signing.BadSignature:
            raise ValidationError('Corrupted or missing state')

        try:
            dropbox_provider = DropboxProvider.objects.get(pk=pk)
        except:
            raise ValidationError('Corrupted or missing dropbox provider')

        try:
            (token, iduser, urlstate) = dbox.dropbox_auth_finish(request.session, request)
        except Exception as e:
            raise ValidationError('dropbox auth failed')

        dropbox_provider.access_token = token
        dropbox_provider.access_user_id = iduser
        dropbox_provider.save()

        provider_pk = dropbox_provider.userstorageaccount_ptr_id
        (check_credentials.si(provider_pk) | resync.si(provider_pk))()

        return HttpResponseRedirect('/home/#/storage_providers')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @detail_route()
    def get_redirect_to_accept_page(self, request, pk):
        """
        Get a redirection URL to Dropbox OAuth authentication page
        :param request:
        :param pk:
        :return:
        """
        dropbox_provider = self.get_object()
        state = signing.dumps({
            'pk': dropbox_provider.pk,
            'user_pk': request.user.pk
        })

        return Response({
            'url': dbox.dropbox_auth_start(request.session, url_state=state)
        })


class B2DropProviderViewSet(ViewsetInjectRequestMixin, ProviderCreateMixin, CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = B2DropProviderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)


class WLWebdavProviderViewSet(ViewsetInjectRequestMixin, ProviderCreateMixin, CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = WLWebdavProviderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)


class UserActionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActionSerializer
    # We don't put IsOwner here, because UserAction doesn't have an owner, but a user (and it is already filtered in
    # get_queryset()
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return UserAction.objects.filter(user=self.request.user)


class ExternalJobPortalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExternalJobPortalSerializer
    permission_class = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ExternalJobPortal.objects.all()


class ExternalJobPortalFormViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExternalJobPortalFormSerializer
    permission_class = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ExternalJobPortalForm.objects.all()


class ExternalJobPortalSubmissionViewSet(ViewsetInjectRequestMixin, CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ExternalJobPortalSubmissionSerializer
    permission_class = (permissions.IsAuthenticated, IsOwner,)

    def get_queryset(self):
        return ExternalJobPortalSubmission.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        v = serializer.save(owner=self.request.user)
        UserAction.log(self.request.user, ACTION_TYPE_JOBPORTAL_SUBMIT, {'portal': v.target.name})

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from serializers import UserSerializer

#from rest_framework import mixins
#retrieving user info from the logged in users with session id - usually sent via cookie
#TODO should be exposed only to localhost queries - queries from another process of the same machine (e.g. Virtual folder metadataservice)
class UserInfo(viewsets.ViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    print >> sys.stderr, "userinfo2"

    #listing will return empty list - TODO - return error
    def list(self, request):
        return Response({})
    #only details can be viewed - routed from /api/vfsession/{sessionid e.g. from cookie}
    def retrieve(self, request, pk=None):
        print >>sys.stderr, "vfsession_detail"+ pk

        session = Session.objects.get(session_key=pk)
        uid = session.get_decoded().get('_auth_user_id')
        #returns user details or HTTP 500 is generated (session matching query doesn exist)
        user = User.objects.get(pk=uid)
        serializer = UserSerializer(user)
        return Response(serializer.data)

