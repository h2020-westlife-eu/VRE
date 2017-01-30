# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


from django.conf import settings
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'datasets', views.DatasetViewSet, base_name='dataset')
router.register(r'datasetfiles', views.DatasetFileViewSet, base_name='datasetfile')
router.register(r'datafiles', views.DatafileViewSet, base_name='datafile')
router.register(r'folders', views.FolderViewSet, base_name='folder')
router.register(r'userstorageaccounts', views.UserStorageAccountViewSet, base_name='userstorageaccount')
router.register(r's3providers', views.S3ProviderViewSet, base_name='s3provider')
router.register(r'gdriveproviders', views.GDriveProviderViewSet, base_name='gdriveprovider')
router.register(r'dropboxproviders', views.DropboxProviderViewSet, base_name='dropboxprovider')
router.register(r'b2dropproviders', views.B2DropProviderViewSet, base_name='b2dropprovider')
router.register(r'wlwebdavproviders', views.WLWebdavProviderViewSet, base_name='wlwebdavprovider')
router.register(r'useractions', views.UserActionViewSet, base_name='useraction')
router.register(r'externaljobportals', views.ExternalJobPortalViewSet, base_name='externaljobportal')
router.register(r'externaljobportalforms', views.ExternalJobPortalFormViewSet, base_name='externaljobportalform')
router.register(r'externaljobportalsubmissions', views.ExternalJobPortalSubmissionViewSet, base_name='externaljobportalsubmission')
router.register(r'vfsession', views.UserInfo,base_name='vfsession')




urlpatterns = [
    url(r'^', include(router.urls)),
]
