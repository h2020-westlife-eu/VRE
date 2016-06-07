# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from contextlib import contextmanager

from rest_framework.test import APITestCase

from api import factories


class BaseAPITestCase(APITestCase):

    def setUp(self):
        self.user = factories.UserFactory.create()
        self.other_user = factories.UserFactory.create()

        self.non_auth_scenario = self.create_scenario(None)
        self.auth_scenario = self.create_scenario(self.user)

    def create_scenario(self, user):
        @contextmanager
        def scenario():
            if user is not None:
                self.client.force_authenticate(user=user)
            yield
            if user is not None:
                self.client.force_authenticate(user=None)

        return scenario


class TestDatafileViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.unvalidated_folder = factories.UnvalidatedFolderFactory.create(owner=self.user)
        self.folder = factories.FolderFactory.create(owner=self.user)
        self.datafile = factories.DatafileFactory.create(owner=self.user, folder=self.folder)
        self.uploaded_datafile = factories.UploadedDatafileFactory.create(owner=self.user, folder=self.folder)

    def test_datafile_get(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/datafiles/', format='json')
            self.assertEquals(response.status_code, 401)

            response = self.client.get('/api/datafiles/%d/' % self.datafile.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/datafiles/', format='json')
            self.assertEquals(response.status_code, 200)

            response = self.client.get('/api/datafiles/%d/' % self.datafile.pk, format='json')
            self.assertEquals(response.status_code, 200)

    def test_datafile_post(self):
        datafile_data = {'filename': 'test_filename', 'folder': self.folder.pk}
        invalid_datafile_data = [
            {'filename': 'test_filename', 'folder': self.unvalidated_folder.pk}
        ]

        with self.non_auth_scenario():
            response = self.client.post('/api/datafiles/', datafile_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/datafiles/', datafile_data, format='json')
            print(response.content)
            self.assertEquals(response.status_code, 201)

            for data in invalid_datafile_data:
                response = self.client.post('/api/datafiles/', data, format='json')
                print(response.content)
                self.assertEquals(response.status_code, 400)

    def test_datafile_put(self):
        datafile_data = {'filename': 'test_filename', 'folder': self.folder.pk}

        with self.non_auth_scenario():
            response = self.client.put('/api/datafiles/%d/' % self.datafile.pk, datafile_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.put('/api/datafiles/%d/' % self.datafile.pk, datafile_data, format='json')
            self.assertEquals(response.status_code, 200)

    def test_datafile_delete(self):
        with self.non_auth_scenario():
            response = self.client.delete('/api/datafiles/%d/' % self.datafile.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.delete('/api/datafiles/%d/' % self.datafile.pk, format='json')
            self.assertEquals(response.status_code, 204)

            response = self.client.delete('/api/datafiles/%d/' % self.uploaded_datafile.pk, format='json')
            self.assertEquals(response.status_code, 204)


class TestFolderViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.folder = factories.FolderFactory.create(owner=self.user)
        self.storage_account = factories.StorageAccountFactory.create(owner=self.user)
        self.root_folder = self.storage_account.get_root_folder()

    def test_folder_get(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/folders/', format='json')
            self.assertEquals(response.status_code, 401)

            response = self.client.get('/api/folders/%d/' % self.folder.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/folders/', format='json')
            self.assertEquals(response.status_code, 200)

            response = self.client.get('/api/folders/%d/' % self.folder.pk, format='json')
            self.assertEquals(response.status_code, 200)

    def test_folder_post(self):
        folder_data = {'name': 'test_folder', 'parent': self.root_folder.pk}
        invalid_folder_data = [
            {'name': 'test_folder', 'parent': None}
        ]

        with self.non_auth_scenario():
            response = self.client.post('/api/folders/', folder_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/folders/', folder_data, format='json')
            print(response.content)
            self.assertEquals(response.status_code, 201)

            for data in invalid_folder_data:
                response = self.client.post('/api/folders/', data, format='json')
                print(response.content)
                self.assertEquals(response.status_code, 400)

    def test_folder_put(self):
        folder_data = {'name': 'test_folder', 'parent': self.root_folder.pk}

        with self.non_auth_scenario():
            response = self.client.put('/api/folders/%d/' % self.folder.pk, folder_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.put('/api/folders/%d/' % self.folder.pk, folder_data, format='json')
            self.assertEquals(response.status_code, 200)

    def test_folder_delete(self):
        with self.non_auth_scenario():
            response = self.client.delete('/api/folders/%d/' % self.folder.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.delete('/api/folders/%d/' % self.folder.pk, format='json')
            self.assertEquals(response.status_code, 204)


class TestUserStorageAccountViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.storage_account = factories.StorageAccountFactory.create(owner=self.user)
        self.root_folder = self.storage_account.get_root_folder()

    def test_userstorageaccount_get(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/userstorageaccounts/', format='json')
            self.assertEquals(response.status_code, 401)

            response = self.client.get('/api/userstorageaccounts/%d/' % self.storage_account.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/userstorageaccounts/', format='json')
            self.assertEquals(response.status_code, 200)

            response = self.client.get('/api/userstorageaccounts/%d/' % self.storage_account.pk, format='json')
            self.assertEquals(response.status_code, 200)

    def test_userstorageaccount_post(self):
        with self.non_auth_scenario():
            response = self.client.post('/api/userstorageaccounts/', format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/userstorageaccounts/', format='json')
            print(response.content)
            self.assertEquals(response.status_code, 405)

    def test_userstorageaccount_put(self):
        with self.non_auth_scenario():
            response = self.client.put('/api/userstorageaccounts/%d/' % self.storage_account.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.put('/api/userstorageaccounts/%d/' % self.storage_account.pk, format='json')
            self.assertEquals(response.status_code, 405)

    def test_userstorageaccount_delete(self):
        with self.non_auth_scenario():
            response = self.client.delete('/api/userstorageaccounts/%d/' % self.storage_account.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.delete('/api/userstorageaccounts/%d/' % self.storage_account.pk, format='json')
            self.assertEquals(response.status_code, 204)


class TestDatasetViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.dataset = factories.DatasetFactory.create(owner=self.user)

    def test_dataset_get(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/datasets/', format='json')
            self.assertEquals(response.status_code, 401)

            response = self.client.get('/api/datasets/%d/' % self.dataset.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/datasets/', format='json')
            self.assertEquals(response.status_code, 200)

            response = self.client.get('/api/datasets/%d/' % self.dataset.pk, format='json')
            self.assertEquals(response.status_code, 200)

    def test_dataset_post(self):
        dataset_data = {'name': 'test_dataset'}
        invalid_dataset_data = []

        with self.non_auth_scenario():
            response = self.client.post('/api/datasets/', dataset_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/datasets/', dataset_data, format='json')
            print(response.content)
            self.assertEquals(response.status_code, 201)

            for data in invalid_dataset_data:
                response = self.client.post('/api/datasets/', data, format='json')
                print(response.content)
                self.assertEquals(response.status_code, 400)

    def test_dataset_put(self):
        dataset_data = {'name': 'test_dataset'}

        with self.non_auth_scenario():
            response = self.client.put('/api/datasets/%d/' % self.dataset.pk, dataset_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.put('/api/datasets/%d/' % self.dataset.pk, dataset_data, format='json')
            self.assertEquals(response.status_code, 200)

    def test_dataset_delete(self):
        with self.non_auth_scenario():
            response = self.client.delete('/api/datasets/%d/' % self.dataset.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.delete('/api/datasets/%d/' % self.dataset.pk, format='json')
            self.assertEquals(response.status_code, 204)

    def test_dataset_publish(self):
        with self.non_auth_scenario():
            response = self.client.post('/api/datasets/%d/publish/' % self.dataset.pk)
            self.assertEquals(response.status_code, 401)

            response = self.client.post('/api/datasets/%d/unpublish/' % self.dataset.pk)
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/datasets/%d/publish/' % self.dataset.pk)
            self.assertEquals(response.status_code, 200)

            # Already published
            response = self.client.post('/api/datasets/%d/publish/' % self.dataset.pk)
            self.assertEquals(response.status_code, 400)

            response = self.client.post('/api/datasets/%d/unpublish/' % self.dataset.pk)
            self.assertEquals(response.status_code, 200)

            # Already unpublished
            response = self.client.post('/api/datasets/%d/unpublish/' % self.dataset.pk)
            self.assertEquals(response.status_code, 400)


class TestDatasetFileViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.dataset_file = factories.DatasetFileFactory.create(owner=self.user)
        self.dataset = factories.DatasetFactory.create(owner=self.user)
        self.datafile = factories.UploadedDatafileFactory.create(owner=self.user)

        self.other_dataset = factories.DatasetFactory.create(owner=self.other_user)
        self.other_datafile = factories.UploadedDatafileFactory.create(owner=self.other_user)
        self.unvalidated_datafile = factories.DatafileFactory.create(owner=self.user)

    def test_datasetfile_get(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/datasetfiles/', format='json')
            self.assertEquals(response.status_code, 401)

            response = self.client.get('/api/datasetfiles/%d/' % self.dataset_file.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/datasetfiles/', format='json')
            self.assertEquals(response.status_code, 200)

            response = self.client.get('/api/datasetfiles/%d/' % self.dataset_file.pk, format='json')
            self.assertEquals(response.status_code, 200)

    def test_datasetfile_post(self):
        datasetfile_data = {'dataset': self.dataset.pk, 'datafile': self.datafile.pk}
        invalid_datasetfile_data = [
            {'dataset': self.dataset.pk},
            {'datafile': self.datafile.pk},
            {'dataset': self.other_dataset.pk, 'datafile': self.datafile.pk},
            {'dataset': self.dataset.pk, 'datafile': self.other_datafile.pk},
            {'dataset': self.other_dataset.pk, 'datafile': self.other_datafile.pk},
            {'dataset': self.other_dataset.pk, 'datafile': self.unvalidated_datafile.pk},
        ]

        with self.non_auth_scenario():
            response = self.client.post('/api/datasetfiles/', datasetfile_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/datasetfiles/', datasetfile_data, format='json')
            print(response.content)
            self.assertEquals(response.status_code, 201)

            for data in invalid_datasetfile_data:
                response = self.client.post('/api/datasetfiles/', data, format='json')
                print(response.content)
                self.assertEquals(response.status_code, 400)

    def test_datasetfile_put(self):
        datasetfile_data = {'dataset': self.dataset.pk, 'datafile': self.datafile.pk}

        with self.non_auth_scenario():
            response = self.client.put('/api/datasetfiles/%d/' % self.dataset_file.pk, datasetfile_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.put('/api/datasetfiles/%d/' % self.dataset_file.pk, datasetfile_data, format='json')
            self.assertEquals(response.status_code, 200)

    def test_datasetfile_delete(self):
        with self.non_auth_scenario():
            response = self.client.delete('/api/datasetfiles/%d/' % self.dataset_file.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.delete('/api/datasetfiles/%d/' % self.dataset_file.pk, format='json')
            self.assertEquals(response.status_code, 204)


class TestUserActionViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.user_action = factories.UserActionFactory.create(user=self.user)

    def test_datasetfile_get(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/useractions/', format='json')
            self.assertEquals(response.status_code, 401)

            response = self.client.get('/api/useractions/%d/' % self.user_action.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/useractions/', format='json')
            self.assertEquals(response.status_code, 200)

            response = self.client.get('/api/useractions/%d/' % self.user_action.pk, format='json')
            self.assertEquals(response.status_code, 200)


class TestGDriveProviderViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.gdriveprovider = factories.UnvalidatedGDriveProviderFactory(owner=self.user)

    def test_gdriveprovider_post(self):
        gdriveprovider_data = {'name': 'New provider'}

        with self.non_auth_scenario():
            response = self.client.post('/api/gdriveproviders/', gdriveprovider_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/gdriveproviders/', gdriveprovider_data, format='json')
            print(response.content)
            self.assertEquals(response.status_code, 201)

    def test_gdriveprovider_get_redirect_to_accept_page(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/gdriveproviders/%d/get_redirect_to_accept_page/' % self.gdriveprovider.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/gdriveproviders/%d/get_redirect_to_accept_page/' % self.gdriveprovider.pk, format='json')
            self.assertEquals(response.status_code, 200)


class TestDropboxProviderViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)
        self.dropboxprovider = factories.UnvalidatedDropboxProviderFactory(owner=self.user)

    def test_dropboxprovider_post(self):
        dropboxprovider_data = {'name': 'New provider'}

        with self.non_auth_scenario():
            response = self.client.post('/api/dropboxproviders/', dropboxprovider_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/dropboxproviders/', dropboxprovider_data, format='json')
            print(response.content)
            self.assertEquals(response.status_code, 201)

    def test_dropboxprovider_get_redirect_to_accept_page(self):
        with self.non_auth_scenario():
            response = self.client.get('/api/dropboxproviders/%d/get_redirect_to_accept_page/' % self.dropboxprovider.pk, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.get('/api/dropboxproviders/%d/get_redirect_to_accept_page/' % self.dropboxprovider.pk, format='json')
            self.assertEquals(response.status_code, 200)


class TestB2DropProviderViewSet(BaseAPITestCase):
    def setUp(self):
        BaseAPITestCase.setUp(self)

    def test_b2dropprovider_post(self):
        b2dropprovider_data = {'name': 'New provider', 'username': 'aaa', 'password': 'bbb'}
        invalid_b2dropprovider_data = [
            {'name': 'New provider', 'username': 'aaa'},
            {'name': 'New provider', 'password': 'bbb'},
        ]

        with self.non_auth_scenario():
            response = self.client.post('/api/b2dropproviders/', b2dropprovider_data, format='json')
            self.assertEquals(response.status_code, 401)

        with self.auth_scenario():
            response = self.client.post('/api/b2dropproviders/', b2dropprovider_data, format='json')
            print(response.content)
            self.assertEquals(response.status_code, 201)

            for data in invalid_b2dropprovider_data:
                response = self.client.post('/api/b2dropproviders/', data, format='json')
                print(response.content)
                self.assertEquals(response.status_code, 400)


class TestViewSets(APITestCase):
    def setUp(self):
        self.user = factories.UserFactory.create()

    def tearDown(self):
        self.client.force_authenticate(user=None)

    def test_dataset_viewset_logged_out(self):
        response = self.client.get('/api/datasets/')

        self.assertEquals(response.status_code, 401)

    def test_dataset_viewset_logged_in(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/datasets/', format='json')

        self.assertEquals(response.status_code, 200)

    def test_datafile_viewset_logged_out(self):
        response = self.client.get('/api/datafiles/')
        self.assertEquals(response.status_code, 401)

    def test_datafile_viewset_logged_in(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/datafiles/', format='json')
        self.assertEquals(response.status_code, 200)

    def test_folder_viewset_logged_out(self):
        response = self.client.get('/api/folders/')
        self.assertEquals(response.status_code, 401)

    def test_folder_viewset_logged_in(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/folders/', format='json')
        self.assertEquals(response.status_code, 200)

    def test_userstorageaccount_viewset_logged_out(self):
        response = self.client.get('/api/userstorageaccounts/')
        self.assertEquals(response.status_code, 401)

    def test_userstorageaccount_viewset_logged_in(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/userstorageaccounts/', format='json')
        self.assertEquals(response.status_code, 200)

    def test_s3provider_viewset_logged_out(self):
        response = self.client.get('/api/s3providers/')
        self.assertEquals(response.status_code, 401)
