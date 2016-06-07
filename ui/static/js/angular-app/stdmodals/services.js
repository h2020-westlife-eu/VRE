angular.module('stdmodals')
    .factory('StdModals', StdModals)
    .factory('DjangoErrors', DjangoErrors);

function StdModals($uibModal) {
    var StdModalsImpl = function () {
        "use strict";
        var that = this;

        /**
         * Opens a modal to ask for confirmation before deleting obj
         * @param obj the object to delete
         * @param delete_function the function to call after confirmation. Will be called as delete_function(obj)
         * @returns {*}
         */
        that.open_delete_modal = function (obj, delete_function) {
            return that.open_confirm_modal('modal_delete_form.html', obj, delete_function);
        };

        /**
         * Opens a modal to ask for confirmation for an action
         * @param form_template the template to use for the modal
         * @param obj the object concerned by the action
         * @param perform_function the function to call after confirmation. Will be call as perform_function(obj)
         * @returns {*}
         */
        that.open_confirm_modal = function (form_template, obj, perform_function) {
            return $uibModal.open({
                templateUrl: form_template,
                controller: 'ModalConfirmActionOnObjectController',
                size: 'lg',
                resolve: {
                    'object': function () {
                        return obj;
                    },
                    'perform_function': function () {
                        return perform_function;
                    }
                }
            }).result;
        };

        /**
         * Opens a modal to create or update an object
         * @param form_template the id of the template to be used for the form
         * @param django_form_name the scope_prefix (dj_<something>, usually) defined in django
         * @param form_name the form_name defined in django
         * @param obj the object to edit, if applicable
         * @param create_update_function the function that will be called after confirmation. Will be called as create_update_function(form_data, obj.pk) or create_update_function(form_data, undefined)
         * @param context a context. Will be made available in the modal controller under $scope.context
         * @returns {*}
         */
        that.open_create_update_modal = function (form_template, django_form_name, form_name, obj, create_update_function, context) {
            return $uibModal.open({
                templateUrl: form_template,
                controller: 'ModalCreateUpdateObjectController',
                size: 'lg',
                resolve: {
                    'django_form_name': function () { return django_form_name; },
                    'form_name': function () { return form_name; },
                    'create_update_function': function () { return create_update_function; },
                    'object': function () { return obj; },
                    'context': function () { return context; }
                }
            }).result;
        };

        /**
         * Opens a simple informative modal
         * @param template the id of the template to use
         * @param context a context. Will be made available in the modal controller under $scope.context
         * @returns {*}
         */
        that.open_modal = function (template, context) {
            return $uibModal.open({
                templateUrl: template,
                controller: 'ModalSimpleController',
                size: 'lg',
                resolve: {
                    'context': function () { return context; }
                }
            }).result;
        };
    };

    return new StdModalsImpl();
}
StdModals.$inject = ['$uibModal'];


function DjangoErrors(djangoForm) {
    "use strict";
    var DjangoErrorsImpl = function () {
        var that = this;

        that.handle_errors = function (form_scope, error) {
            if (angular.isDefined(error.data) && !_.isString(error.data)) {
                djangoForm.setErrors(form_scope, error.data);
            } else {
                djangoForm.setErrors(form_scope, {'__all__': ['An unexpected error occured']});
            }
        };
    };

    return new DjangoErrorsImpl();
}
DjangoErrors.$inject = ['djangoForm'];
