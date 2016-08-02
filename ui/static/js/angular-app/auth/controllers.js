angular.module('auth')
    .controller('LoginController', LoginController)
    .controller('LogoutController', LogoutController)
    .controller('RegisterController', RegisterController)
    .controller('ForgotPasswordController', ForgotPasswordController)
    .controller('ResetPasswordController', ResetPasswordController)
    .controller('ProfileController', ProfileController);

function LoginController($scope, $location, $rootScope, DjangoErrors, AuthenticationService, DatasetManager, StorageContentsManager, AppSettingsService) {
    "use strict";

    /*
    $scope.submit = function (data) {
        return AuthenticationService.login(data.username, data.password).then(
            function (res) {
                if (AuthenticationService.is_logged_in()) {
                    StorageContentsManager.load();
                    DatasetManager.load();
                    $location.path('/main');
                }
            },
            function (error) {
                DjangoErrors.handle_errors($scope.login_form, error);
            }
        );
    };
    */
    $rootScope.$on('login', function () {
        $location.path('/main');
    });

    $scope.enable_register = AppSettingsService.ENABLE_REGISTER;

}
LoginController.$inject = ['$scope', '$location', '$rootScope', 'DjangoErrors', 'AuthenticationService', 'DatasetManager', 'StorageContentsManager', 'AppSettingsService'];


function LogoutController($location, AuthenticationService) {
    "use strict";

    AuthenticationService.logout().then(
        function () {
            $location.path('/login');
        }
    );
}
LogoutController.$inject = ['$location', 'AuthenticationService'];


function RegisterController($scope, $location, AuthenticationService, DjangoErrors) {
    "use strict";
    $scope.submit = function (data) {
        return AuthenticationService.register(data).then(
            function (res) {
                if (AuthenticationService.is_logged_in()) {
                    $location.path('/');
                }
            },
            function (error) {
                DjangoErrors.handle_errors($scope.register_form, error);
            }
        );
    };
}
RegisterController.$inject = ['$scope', '$location', 'AuthenticationService', 'DjangoErrors'];


function ForgotPasswordController($scope, $location, AuthenticationService, DjangoErrors) {
    "use strict";
    $scope.submit = function (data) {
        return AuthenticationService.forgotPassword(data).then(
            function () {
                $location.path('/login');
            },
            function (error) {
                DjangoErrors.handle_errors($scope.forgot_password_form, error);
            }
        );
    };
}
ForgotPasswordController.$inject = ['$scope', '$location', 'AuthenticationService', 'DjangoErrors'];


function ResetPasswordController($scope, $routeParams, $http, $location, djangoForm, MessageManager) {
    "use strict";
    $scope.token = $routeParams.token;
    $scope.uid = $routeParams.uid;

    $scope.submit = function (data) {
        return $http.post(
            '/auth/password/reset/confirm/',
            {uid: $scope.uid, token: $scope.token, new_password: data.new_password, re_new_password: data.re_new_password}
        ).then(
            function (res) {
                $location.path('/login/');
                MessageManager.toggleMessage('passwordResetSuccess');
            },
            function (error) {
                if (angular.isDefined(error.data.__all__) && error.data.__all__ === 'Invalid token for given user.') {
                    error.data.__all__ = ['An error occured, you need to request a new email to reset your password.'];
                }
                djangoForm.setErrors($scope.reset_password_form, error.data);
            }
        );
    };
}
ResetPasswordController.$inject = ['$scope', '$routeParams', '$http', '$location', 'djangoForm', 'MessageManager'];


function ProfileController(AuthenticationService, StdModals, MessageManager) {
    "use strict";
    var self = this;
    self.user = AuthenticationService.user_info;
    self.messages = MessageManager.messages;

    self.openChangePasswordModal = function () {
        StdModals.open_create_update_modal(
            'change_password.html',
            'dj_change_password',
            'change_password_form',
            undefined,
            AuthenticationService.changePassword
        );
    };

}
ProfileController.$inject = ['AuthenticationService', 'StdModals', 'MessageManager'];
