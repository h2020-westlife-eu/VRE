angular.module('pype.datasets')
    .controller('DatasetsController', DatasetsController)
    .controller('ExplorerController', ExplorerController)
    /*
    .controller('DatasetCreateController', DatasetCreateController)
    .controller('DatafileCreateController', DatafileCreateController)
    */

    .controller('StorageProvidersController', StorageProvidersController)
    .controller('TasksController', TasksController)
    .controller('MenuController', MenuController)
    .controller('UserActionController', UserActionController)
    .controller('SelectFileController', SelectFileController);

function ExplorerController($scope, stdModals, StorageContentsManager, UploadTasksManager, isRootFolderFilter) {
    "use strict";
    $scope.folders = StorageContentsManager.getFolders();
    $scope.root_folders = [];
    $scope.active_folder = undefined;
    $scope.active_datafiles = [];

    $scope.folders_collapse = [];

    $scope.$watch(
        'folders',
        function (newval, oldval) {
            // Set the folders_collapse value for all folders
            _.forEach(newval, function (value) { $scope.folders_collapse[value.pk] = true; });

            // Update the list of root folders
            $scope.root_folders = isRootFolderFilter(newval);

            // Expand the root folders
            _.forEach($scope.root_folders, function (value) { $scope.folders_collapse[value.pk] = false; });
        },
        true
    );

    $scope.$watch(
        'active_folder',
        function (newval, oldval) {
            $scope.active_datafiles = StorageContentsManager.getFiles(newval);
        }
    );

    $scope.select_folder = function (folder) {
        if (angular.isUndefined(folder)) {
            return;
        }

        $scope.active_folder = folder;
        $scope.active_folder_pk = folder.pk;
        $scope.folders_collapse[folder.pk] = false;
    };

    $scope.switch_collapse_folder = function (folder) {
        $scope.folders_collapse[folder.pk] = !$scope.folders_collapse[folder.pk];
    };

    $scope.open_create_datafile_modal = function (folderId) {
        var context = {
            'upload_file': null
        };

        stdModals.open_create_update_modal(
            'datafile_form.html',
            'dj_datafile',
            'datafile_form',
            undefined,
            function (data, pk) {
                return StorageContentsManager.create_datafile({'filename': context.upload_file.name}, pk, folderId);
            },
            context
        ).then(
            function (rep) {
                // We refresh the display a first time, so that it appears as "Transfer in progress"
                $scope.active_datafiles = StorageContentsManager.getFiles($scope.active_folder);

                // Start the upload
                UploadTasksManager.create_upload_task(rep.pk, context.upload_file.name, context.upload_file).then(
                    function () {
                        // Refresh datafile and then update the display
                        StorageContentsManager.refreshDatafile(rep.pk).then(
                            function () {
                                $scope.active_datafiles = StorageContentsManager.getFiles($scope.active_folder);
                            }
                        );
                    }
                );
            }
        );
    };

    $scope.open_update_datafile_modal = function (datafile) {
        stdModals.open_create_update_modal(
            'datafile_update_form.html',
            'dj_datafile_update',
            'datafile_update_form',
            datafile,
            function (data, pk) { return StorageContentsManager.create_datafile(data, pk, datafile.dataset); }
        ).then(
            function () {
                $scope.active_datafiles = StorageContentsManager.getFiles($scope.active_folder);
            }
        );
    };


    $scope.open_delete_datafile_modal = function (obj) {
        stdModals.open_delete_modal(obj, StorageContentsManager.delete_datafile).then(
            function () {
                $scope.active_datafiles = StorageContentsManager.getFiles($scope.active_folder);
            }
        );
    };

    $scope.open_create_folder_modal = function (parentFolderId) {
        stdModals.open_create_update_modal(
            'folder_form.html',
            'dj_folder',
            'folder_form',
            undefined,
            function (data, pk) { return StorageContentsManager.create_folder(data, pk, parentFolderId); }
        );
    };

    $scope.refresh = function () {
        return StorageContentsManager.refresh().then(
            function () {
                $scope.active_datafiles = StorageContentsManager.getFiles($scope.active_folder);
            }
        );
    };

    $scope.refresh_storage_account = function (account) {
        return StorageContentsManager.refreshStorageAccount(account).then(
            function () {
                $scope.active_datafiles = StorageContentsManager.getFiles($scope.active_folder);
            }
        );
    };

    $scope.refresh_folder = function (folder) {
        var account = StorageContentsManager.getStorageAccountForFolder(folder);
        if (angular.isDefined(account)) {
            return StorageContentsManager.refreshStorageAccount(account).then(
                function () {
                    $scope.active_datafiles = StorageContentsManager.getFiles($scope.active_folder);
                }
            );
        }
    };

    $scope.disable_refresh_folder = function (folder) {
        var account = StorageContentsManager.getStorageAccountForFolder(folder);
        return account.sync_in_progress;
    };

}
ExplorerController.$inject = ['$scope', 'StdModals', 'StorageContentsManager', 'UploadTasksManager', 'isRootFolderFilter'];


function DatasetsController($scope, $window, stdModals, DatasetManager, StorageProviderManager, UploadTasksManager, pk) {
    "use strict";
    $scope.datasets = DatasetManager.getAll();

    $scope.active_dataset = undefined;
    $scope.active_dataset_pk = undefined;
    $scope.active_datafiles = [];

    $scope.select_dataset = function (dataset) {
        if (angular.isUndefined(dataset)) {
            return;
        }

        $scope.active_dataset = dataset;
        $scope.active_dataset_pk = dataset.pk;

        $scope.active_datafiles = DatasetManager.datafilesForDataset(dataset);
    };

    if (!angular.isUndefined(pk)) {
        $scope.select_dataset(DatasetManager.getDatasetById(pk));
    }

    $scope.open_delete_dataset_modal = function (obj) {
        stdModals.open_delete_modal(obj, DatasetManager.delete_dataset);
    };

    $scope.open_create_dataset_modal = function () {
        stdModals.open_create_update_modal(
            'dataset_form.html',
            'dj_dataset',
            'dataset_form',
            undefined,
            DatasetManager.create_dataset
        );
    };

    $scope.open_update_dataset_modal = function (dataset) {
        stdModals.open_create_update_modal(
            'dataset_form.html',
            'dj_dataset',
            'dataset_form',
            dataset,
            DatasetManager.create_dataset
        );
    };

    $scope.open_publish_dataset_modal = function (dataset) {
        stdModals.open_confirm_modal(
            'dataset_publish.html',
            dataset,
            DatasetManager.publish_dataset
        );
    };

    $scope.open_unpublish_dataset_modal = function (dataset) {
        stdModals.open_confirm_modal(
            'dataset_unpublish.html',
            dataset,
            DatasetManager.unpublish_dataset
        );
    };

    $scope.open_add_datafile_to_dataset_modal = function (dataset) {
        //stdModals.open_modal('select_file_widget.html');

        stdModals.open_create_update_modal(
            'select_file_form.html',
            'dj_dataset_add_file',
            'dataset_add_file_form',
            undefined,
            function (data) { return DatasetManager.add_file_to_dataset(dataset, data); }
        ).then(
            function () {
                $scope.active_datafiles = DatasetManager.datafilesForDataset($scope.active_dataset);
            }
        );
    };

    $scope.open_share_url_modal = function (dataset) {
        var origin = $window.location.protocol + "//" + $window.location.hostname + ($window.location.port ? ':' + $window.location.port : '');
        var share_url = origin + '/api/datasets/download/?publish_key=' + dataset.publish_key;
        stdModals.open_modal('dataset_share_url_modal.html', {'share_url': share_url});
    };

}
DatasetsController.$inject = ['$scope', '$window', 'StdModals', 'DatasetManager', 'StorageProviderManager', 'UploadTasksManager', 'pk'];


function StorageProvidersController($scope, $http, $window, stdModals, StorageProviderManager) {
    "use strict";
    $scope.storage_accounts = StorageProviderManager._all_user_storage_accounts;

    $scope.open_create_s3_provider_modal = function () {
        stdModals.open_create_update_modal(
            's3provider_form.html',
            'dj_s3provider',
            's3provider_form',
            undefined,
            StorageProviderManager.create_s3_provider
        );
    };

    $scope.open_create_gdrive_provider_modal = function () {
        stdModals.open_create_update_modal(
            'gdriveprovider_form.html',
            'dj_gdriveprovider',
            'gdriveprovider_form',
            undefined,
            StorageProviderManager.create_gdrive_provider
        ).then(
            function (rep) {
                $http.get('/api/gdriveproviders/' + rep.pk + '/get_redirect_to_accept_page/').then(
                    function (rep) {
                        if (angular.isDefined(rep.data.url)) {
                            $window.location.href = rep.data.url;
                        } else {
                            console.log('Redirect page location is undefined!');
                        }
                    },
                    function () {
                        console.log('Error getting redirection!');
                    }
                );
            }
        );
    };

    $scope.open_create_dropbox_provider_modal = function () {
        stdModals.open_create_update_modal(
            'dropboxprovider_form.html',
            'dj_dropboxprovider',
            'dropboxprovider_form',
            undefined,
            StorageProviderManager.create_dropbox_provider
        ).then(
            function (rep) {
                $http.get('/api/dropboxproviders/' + rep.pk + '/get_redirect_to_accept_page/').then(
                    function (rep) {
                        console.log('TODO', rep);
                        if (angular.isDefined(rep.data.url)) {
                            $window.location.href = rep.data.url;
                        } else {
                            console.log('Redirect page location is undefined!');
                        }
                    },
                    function () {
                        console.log('Error getting redirection!');
                    }
                );
            }
        );
    };

    $scope.open_create_b2drop_provider_modal = function () {
        stdModals.open_create_update_modal(
            'b2dropprovider_form.html',
            'dj_b2dropprovider',
            'b2dropprovider_form',
            undefined,
            StorageProviderManager.create_b2drop_provider
        );
    };

    $scope.open_create_wlwebdav_provider_modal = function () {
        stdModals.open_create_update_modal(
            'wlwebdavprovider_form.html',
            'dj_wlwebdavprovider',
            'wlwebdavprovider_form',
            undefined,
            StorageProviderManager.create_wlwebdav_provider
        );
    };

    $scope.open_delete_provider_modal = function (obj) {
        stdModals.open_delete_modal(obj, StorageProviderManager.delete_provider);
    };

    $scope.refresh = function () {
        return StorageProviderManager.refresh();
    };
}
StorageProvidersController.$inject = ['$scope', '$http', '$window', 'StdModals', 'StorageProviderManager'];


function TasksController($scope, UploadTasksManager) {
    "use strict";
    $scope.active_tasks = UploadTasksManager.active_tasks;

}
TasksController.$inject = ['$scope', 'UploadTasksManager'];


function MenuController(AuthenticationService) {
    "use strict";
    var that = this;
    that.authenticationService = AuthenticationService;
}
MenuController.$inject = ['AuthenticationService'];


function UserActionController($scope, UserAction) {
    "use strict";
    var that = this;

    $scope.actions = UserAction.loadAll();

}
UserActionController.$inject = ['$scope', 'UserAction'];


function SelectFileController($scope, StorageContentsManager, isRootFolderFilter) {
    "use strict";

    $scope.folders = StorageContentsManager.getFolders();
    $scope.root_folders = [];
    $scope.active_folder = undefined;
    $scope.active_datafiles = [];
    $scope.active_subfolders = [];

    $scope.selected_file = undefined;

    $scope.$watch(
        'folders',
        function (newval, oldval) {
            // Update the list of root folders
            $scope.root_folders = isRootFolderFilter(newval);
        },
        true
    );

    $scope.$watch(
        'active_folder',
        function (newval, oldval) {
            console.log('active_folder changed from', oldval, 'to', newval);
            $scope.active_datafiles = StorageContentsManager.getFiles(newval);
            $scope.active_subfolders = StorageContentsManager.getSubFolders(newval);
        }
    );

    StorageContentsManager.loadPromise.then(
        function () {
            $scope.active_datafiles = StorageContentsManager.getFiles();
            $scope.active_subfolders = StorageContentsManager.getSubFolders();
        }
    );

    $scope.active_folder = null;

    $scope.select_folder_by_id = function (folder_pk) {
        var folder = StorageContentsManager.getFolderById(folder_pk);
        $scope.select_folder(folder);
    };

    $scope.select_folder = function (folder) {
        if (angular.isUndefined(folder)) {
            $scope.active_folder = undefined;
            $scope.active_folder_pk = undefined;
            return;
        }

        $scope.active_folder = folder;
        $scope.active_folder_pk = folder.pk;
    };

    $scope.select_file = function (datafile) {
        $scope.selected_file = datafile;
    };

    $scope.submit = function () {
        return $scope.create_update_function($scope.selected_file).then(
            function (data) {
                $scope.close(data);
                return data;
            },
            function (error) {
                // DjangoErrors.handle_errors($scope.dataset_add_file_form, error);
                $scope.dataset_add_file_form.error = {};
                $scope.dataset_add_file_form.error.$message = error.data['datafile'];
                console.log('Adding file to dataset failed:', error);
            }
        );
    };
}
SelectFileController.$inject = ['$scope', 'StorageContentsManager', 'isRootFolderFilter'];
