angular.module('pype.datasets')
    .factory('DatasetManager', DatasetManager)
    .factory('StorageContentsManager', StorageContentsManager)
    .factory('StorageProviderManager', StorageProviderManager)
    .factory('UploadTasksManager', UploadTasksManager);

function DatasetManager(Dataset, DatasetFile) {
    "use strict";
    var DatasetManagerCl = function () {
        var that = this;

        that._all_datasets = [];
        that._all_datasetfiles = [];

        that.load = function () {
            that._all_datasets = Dataset.loadAll();
            that._all_datasetfiles = DatasetFile.loadAll();
        };

        that.getAll = function () {
            return that._all_datasets;
        };

        that.datafilesForDataset = function (dataset) {
            return _.filter(
                that._all_datasetfiles,
                function (datasetfile) {
                    return datasetfile.dataset === dataset.pk;
                }
            );
        };

        that.getDatasetById = function (dataset_pk) {
            return Dataset.getById(dataset_pk);
        };

        that.create_dataset = Dataset.create;

        that.delete_dataset = Dataset.delete;

        that.publish_dataset = function (dataset) {
            return dataset.$publish();
        };

        that.unpublish_dataset = function (dataset) {
            return dataset.$unpublish();
        };

        that.add_file_to_dataset = function (dataset, datafile) {
            console.log('Adding', datafile.filename, 'to', dataset.name);

            return DatasetFile.create({
                'dataset': dataset.pk,
                'datafile': datafile.pk
            });
        };
    };

    var dm = new DatasetManagerCl();

    dm.load();

    return dm;
}
DatasetManager.$inject = ['Dataset', 'DatasetFile'];


function StorageContentsManager($q, Datafile, Folder, UserStorageAccount, isRootFolderFilter, fileIsInFolderFilter, folderIsSubfolderOfFilter) {
    "use strict";
    var StorageContentsManagerCl = function () {
        var that = this;

        that._all_datafiles = [];
        that._all_folders = [];
        that._all_user_storage_accounts = [];
        that.loadPromise = undefined;

        that.load = function () {
            that._all_datafiles = Datafile.loadAll();
            that._all_folders = Folder.loadAll();
            that._all_user_storage_accounts = UserStorageAccount.loadAll();

            that.loadPromise = $q.all([
                that._all_datafiles.$promise,
                that._all_folders.$promise,
                that._all_user_storage_accounts.$promise
            ]);
        };

        that.refreshStorageAccount = function (account) {
            return account.$resync().then(
                function () {
                    return $q.all(
                        Datafile.refreshAll(),
                        Folder.refreshAll()
                    );
                }
            );
        };

        that.refresh = function () {
            // Call resync on all active UserStorageAccount
            return $q.all(
                _.map(
                    _.filter(that._all_user_storage_accounts, function (d) { return d.validated; }),
                    function (account) { return account.$resync(); }
                )
            ).then(
                function () {
                    return $q.all(
                        Datafile.refreshAll(),
                        Folder.refreshAll()
                    );
                }
            );
        };

        that.getFolders = function () {
            return that._all_folders;
        };

        that.getStorageAccountForFolder = function (folder) {
            return _.find(that._all_user_storage_accounts, function (d) { return d.pk === folder.storage_account; });
        };

        that.getFolderById = function (pk) {
            return Folder.getById(pk);
        };

        that.getRootFolders = function () {
            return isRootFolderFilter(that._all_folders);
        };

        that.getFiles = function (folder) {
            if (angular.isUndefined(folder) || folder === null) {
                return [];
            } else {
                return fileIsInFolderFilter(that._all_datafiles, folder);
            }
        };

        that.getSubFolders = function (folder) {
            if (angular.isUndefined(folder) || folder === null) {
                return that.getRootFolders();
            } else {
                return folderIsSubfolderOfFilter(that._all_folders, folder);
            }
        };

        that.refreshDatafile = function (datafile_pk) {
            return Datafile.refreshOne(datafile_pk);
        };

        that.create_datafile = function (data, pk, folderId) {
            return Datafile.create(data, pk, {folder: folderId});
        };

        that.delete_datafile = Datafile.delete;

        that.create_folder = function (data, pk, parentFolderId) {
            return Folder.create(data, pk, {parent: parentFolderId});
        };
    };

    var scm = new StorageContentsManagerCl();
    scm.load();

    return scm;

}
StorageContentsManager.$inject = ['$q', 'Datafile', 'Folder', 'UserStorageAccount', 'isRootFolderFilter', 'fileIsInFolderFilter', 'folderIsSubfolderOfFilter'];


function StorageProviderManager($q, UserStorageAccount, S3Provider, GDriveProvider, B2DropProvider, DropboxProvider) {
    "use strict";
    var StorageProviderManagerCl = function () {
        var that = this;

        that._all_user_storage_accounts = [];
        //that._all_s3_providers = [];

        that.load = function () {
            that._all_user_storage_accounts = UserStorageAccount.loadAll();
            //that._all_s3_providers = S3Provider.loadAll();

            // Return a promise that fires once everything is done loading
            return $q.all([
                that._all_user_storage_accounts.$promise,
                //that._all_s3_providers.$promise
            ]).then(
                function () {
                    return that;
                }
            );
        };

        that.refresh = UserStorageAccount.refreshAll;

        /*
         ** UNUSED
        that.get_validated_storage_providers = function () {
            return _.filter(
                that._all_user_storage_accounts,
                function (account) {
                    return account.validated === true;
                }
            );
        };
        */

        that.create_s3_provider = function (data, pk) {
            return S3Provider.create(data, pk).then(
                function (rep) {
                    UserStorageAccount.refreshAll();
                    return rep;
                }
            );
        };

        that.create_gdrive_provider = function (data, pk) {
            return GDriveProvider.create(data, pk).then(
                function (rep) {
                    UserStorageAccount.refreshAll();
                    return rep;
                }
            );
        };

        that.create_dropbox_provider = function (data, pk) {
            return DropboxProvider.create(data, pk).then(
                function (rep) {
                    UserStorageAccount.refreshAll();
                    return rep;
                }
            );
        };

        that.create_b2drop_provider = function (data, pk) {
            return B2DropProvider.create(data, pk).then(
                function (rep) {
                    UserStorageAccount.refreshAll();
                    return rep;
                }
            );
        };

        that.delete_provider = UserStorageAccount.delete;
    };

    var smc = new StorageProviderManagerCl();

    smc.load();

    return smc;
}
StorageProviderManager.$inject = ['$q', 'UserStorageAccount', 'S3Provider', 'GDriveProvider', 'B2DropProvider', 'DropboxProvider'];


function UploadTasksManager($q, Upload) {
    "use strict";
    var UploadTask = function (datafile_pk, filename, upload_file) {
        var that = this;

        that.datafile_pk = datafile_pk;
        that.filename = filename;
        that.upload_file = upload_file;

        that.progress = 0;
        that.done = false;
        that.success = true;

        that.set_progress = function (progress) {
            that.progress = progress;
        };

        that.start_upload = function () {
            return Upload.upload({
                url: '/api/datafiles/' + that.datafile_pk + '/upload/',
                data: {file: that.upload_file}
            }).then(
                function (response) {
                    that.done = true;
                    // SUCCESS!
                },
                function (response) {
                    that.done = true;
                    that.success = false;
                    // FAILURE!
                },
                function (evt) {
                    var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                    that.set_progress(progressPercentage);
                    // console.log('Uploaded', evt.loaded, 'out of', evt.total);
                }
            );
        };
    };

    var UploadTaskManagerCl = function () {
        var that = this;

        that.active_tasks = [];

        that.has_active_tasks = function () {
            return that.active_tasks.length > 0;
        };

        /**
         * Initiates a background upload of a file and returns a promise that fires when the upload is done
         * @param datafile_pk
         * @param filename
         * @param upload_file
         * @returns {*}
         */
        that.create_upload_task = function (datafile_pk, filename, upload_file) {
            var task = new UploadTask(datafile_pk, filename, upload_file);
            that.active_tasks.push(task);

            return task.start_upload().then(
                function (rep) {
                    // TODO: On completion, remove from list
                },
                function (rep) {
                    // TODO: On completion, remove from list
                }
            );
        };

    };

    var utm = new UploadTaskManagerCl();

    return utm;
}
UploadTasksManager.$inject = ['$q', 'Upload'];

