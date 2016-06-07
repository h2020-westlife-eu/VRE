angular.module('pype.jobportals')
    .controller('ExploreJobPortalsController', ExploreJobPortalsController)
    .controller('JobsController', JobsController);


function ExploreJobPortalsController($scope, ExternalJobPortalForm) {
    "use strict";

    $scope.active_form = undefined;
    $scope.all_forms = ExternalJobPortalForm.loadAll();

    $scope.select_form = function (form) {
        $scope.active_form = form;
    };

}
ExploreJobPortalsController.$inject = ['$scope', 'ExternalJobPortalForm'];


function JobsController($scope) {
    "use strict";

}
JobsController.$inject = ['$scope'];
