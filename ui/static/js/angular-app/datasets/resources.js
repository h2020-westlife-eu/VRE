(function () {
    "use strict";

    /* The pattern used by the urls */
    var gen_url = _.template('/api/<%= url_name %>/:pk/:action/');

    /* The list of resources that the server supports */
    var resources = [
        ['Dataset', 'datasets',
            {
                'publish': {method: 'POST', params: {action: 'publish'}},
                'unpublish': {method: 'POST', params: {action: 'unpublish'}}
            }],
        ['DatasetFile', 'datasetfiles'],
        ['Datafile', 'datafiles'],
        ['Folder', 'folders'],
        ['UserStorageAccount', 'userstorageaccounts',
            {
                'resync': {method: 'POST', params: {action: 'resync'}}
            }],
        ['S3Provider', 's3providers'],
        ['GDriveProvider', 'gdriveproviders'],
        ['DropboxProvider', 'dropboxproviders'],
        ['B2DropProvider', 'b2dropproviders'],
        ['UserAction', 'useractions'],
        ['ExternalJobPortal', 'externaljobportals'],
        ['ExternalJobPortalForm', 'externaljobportalforms'],
        ['ExternalJobPortalSubmission', 'externaljobportalsubmissions']
    ];


    // Backend-specific configuration ends here
    // ----------------------------------------------------------------------
    var module = angular.module('pype.datasets')

        .config(['$resourceProvider', function ($resourceProvider) {
            // Don't strip trailing slashes from calculated URLs
            $resourceProvider.defaults.stripTrailingSlashes = false;
        }]);

    angular.forEach(resources, function (resource) {
        var rest_resource_name = resource[0] + 'Res';

        if (angular.isUndefined(resource[2])) {
            resource[2] = {};
        }
        _.merge(resource[2], {'update': {method: 'PUT'}});

        module.factory(rest_resource_name, ['$resource', function ($resource) {
            var resource_url = gen_url({'url_name': resource[1]});
            return $resource(resource_url, {'pk': '@pk'}, resource[2]);
        }]);

        module.factory(resource[0], [rest_resource_name, '$q', '$rootScope', 'LunaWebsocketsService', function (RestResource, $q, $rootScope, LunaWebsocketsService) {
            var ResourceImpl = function () {
                var that = this;

                that._all = [];

                that.loadAll = function () {
                    that._all = RestResource.query();
                    return that._all;
                };

                that.getAll = function () {
                    return that._all;
                };

                that.getById = function (pk) {
                    return _.find(that._all, function (d) {return d.pk === pk; });
                };

                that.refreshOne = function (pk) {
                    return RestResource.get({pk: pk}).$promise.then(
                        function (res) {
                            that.refreshOneData(pk, res);
                        }
                    );
                };

                that.refreshOneData = function (pk, data) {
                    that._all[_.findIndex(that._all, function (d) {
                        return d.pk === pk;
                    })] = data;
                };

                that.refreshAll = function () {
                    var q = RestResource.query().$promise.then(
                        function (data) {
                            that.refreshAllData(data);
                        }
                    );
                    that._all.$promise = q.$promise;
                };

                that.refreshAllData = function (data) {
                    that.reset();
                    _.each(data, function (val) { that._all.push(val); });
                };

                that.appendOneData = function (data) {
                    that._all.push(data);
                };

                that.reset = function () {
                    _.remove(that._all, function (d) { return true; });
                };

                that.create = function (data, pk, attrs) {
                    var new_resource = new RestResource(data);

                    // Assign any supplementary attributes
                    _.forIn(attrs, function (value, key) {
                        // Don't overwrite any existing value with undefined
                        if (angular.isDefined(value)) {
                            new_resource[key] = value;
                        }
                    });

                    if (angular.isDefined(pk)) {
                        new_resource.pk = pk;
                        return new_resource.$update().then(
                            function (res) {
                                that.refreshOneData(pk, res);
                                return res;
                            },
                            function (res) {
                                return $q.reject(res);
                            }
                        );
                    } else {
                        return new_resource.$save().then(
                            function (res) {
                                that.appendOneData(res);
                                return res;
                            },
                            function (res) {
                                return $q.reject(res);
                            }
                        );
                    }
                };

                that.delete = function (obj) {
                    if (angular.isUndefined(obj)) {
                        return;
                    }

                    return obj.$delete().then(
                        function (res) {
                            _.remove(that._all, function (d) { return d.pk === res.pk; });
                            return res;
                        },
                        function (res) {
                            return $q.reject(res);
                        }
                    );
                };

                $rootScope.$on('logout', function (e, d) { that.reset(); });

                LunaWebsocketsService.subscribe('model.' + resource[0] + '.updateOne', function (data) {
                    that.refreshOneData(data.pk, new RestResource(data));
                });

            };

            return new ResourceImpl();
        }]);

    });

}());
