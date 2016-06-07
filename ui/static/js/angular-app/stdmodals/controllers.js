angular.module('stdmodals')
    .controller('ModalConfirmActionOnObjectController', ModalConfirmActionOnObjectController)
    .controller('ModalCreateUpdateObjectController', ModalCreateUpdateObjectController)
    .controller('ModalSimpleController', ModalSimpleController);


/**
 * A controller for a Confirm modal
 * @param $scope
 * @param $uibModalInstance
 * @param $q
 * @param object: the object we are interacting with
 * @param perform_function: the delete function. Called as: perform_function(object). Must return a promise.
 * @constructor
 */
function ModalConfirmActionOnObjectController($scope, $uibModalInstance, $q, object, perform_function) {
    "use strict";
    $scope.object = object;

    $scope.dismiss = $uibModalInstance.dismiss;

    $scope.submit = function () {
        return perform_function($scope.object).then(
            function (data) {
                $uibModalInstance.close(data);
                return data;
            },
            function (data) {
                console.log('Perform_function failed!');
                return $q.reject(data);
            }
        );
    };
}
ModalConfirmActionOnObjectController.$inject = ['$scope', '$uibModalInstance', '$q', 'object', 'perform_function'];


/**
 * A controller for a Create/Update modal
 * @param $scope
 * @param $uibModalInstance
 * @param DjangoErrors
 * @param django_form_name: the value of "scope_prefix" on the django side
 * @param form_name: the value of the "name" attribute on the form
 * @param object: to edit an existing object, pass the existing value here. Otherwise, pass undefined. This object will be used for initial values of the form. It must also have a pk
 * @param create_update_function: the create/update function. Called as: create_function(new_data, pk), where pk can be undefined (in case of a creation)
 * @param context: an arbitrary object. Will be put in the modal's scope as $scope.context. Useful for, for example, ModelChoiceFields choices
 * @constructor
 */
function ModalCreateUpdateObjectController($scope, $timeout, $uibModalInstance, DjangoErrors, django_form_name, form_name, object, create_update_function, context) {
    "use strict";
    $scope.context = context;
    $scope.existing_obj = _.cloneDeep(object);  // We need to clone the object here, otherwise editing the value in the form would change the existing object!

    if (angular.isUndefined($scope.existing_obj)) {
        $scope.pk = undefined;
    } else {
        /* Wrap this in a $timeout to solve obscure angular behaviour. */
        $timeout(function() {
            $scope[django_form_name] = $scope.existing_obj;
        }, 0);
        $scope.pk = $scope.existing_obj.pk;
    }

    $scope.dismiss = $uibModalInstance.dismiss;

    /* Focus on the first input of the form */
    // TODO: What if there is no input ?
    $uibModalInstance.opened.then(function () {
        $timeout(function () {
            angular.element('input')[0].focus();
        }, 500);
    });

    $scope.submit = function (data) {
        return create_update_function(data, $scope.pk).then(
            function (data) {
                $uibModalInstance.close(data);
                return data;
            },
            function (error) {
                DjangoErrors.handle_errors($scope[form_name], error);
            }
        );
    };
}
ModalCreateUpdateObjectController.$inject = ['$scope', '$timeout', '$uibModalInstance', 'DjangoErrors', 'django_form_name', 'form_name', 'object', 'create_update_function', 'context'];


function ModalSimpleController($scope, $uibModalInstance, context) {
    "use strict";
    $scope.context = context;

    $scope.dismiss = $uibModalInstance.dismiss;
    $scope.close = $uibModalInstance.close;

}
ModalSimpleController.$inject = ['$scope', '$uibModalInstance', 'context'];
