angular.module('auth')
    .factory('AuthenticationService', AuthenticationService);


function AuthenticationService($http, $window, $q, $rootScope, MessageManager) {
    var authservice = {};

    authservice.auth_token = undefined;
    authservice.user_info = undefined;
    authservice.loadPromise = $q.defer();

    authservice.waitForLoad = function () {
        "use strict";
        return authservice.loadPromise.promise.then(function () {
            return authservice;
        });
    };

    authservice.login_with_token = function (auth_token) {
        authservice.auth_token = auth_token;
        $http.defaults.headers.common.Authorization = 'Token ' + authservice.auth_token;

        $http.get('/auth/me/').then(
            function (data) {
                authservice.user_info = {
                    'id': data.data.id,
                    'username': data.data.username,
                    'email': data.data.email,
                    'created_at': 0
                };

                $rootScope.$emit('login', authservice.user_info);

                authservice.loadPromise.resolve(data);
            },
            function () {
                authservice.logout_with_token();
                // Note: We don't reject the promise here! A failed login just means waitForLoad() keeps waiting
            }
        );
        return authservice.loadPromise.promise;
    };

    authservice.logout_with_token = function () {
        authservice.auth_token = undefined;
        authservice.user_info = undefined;
        authservice.loadPromise = $q.defer();  // Reset the loadPromise
        $http.defaults.headers.common.Authorization = undefined;
        $window.localStorage.setItem('auth_token', null);
        $window.location.reload();
    };

    authservice.login = function (username, password) {
        return $http.post(
            '/auth/login/',
            {'username': username, 'password': password},
            {headers: { 'Authorization': undefined }}
        ).then(
            function (data) {
                return authservice.login_with_token(data.data.auth_token).then(
                    function () {
                        $window.localStorage.setItem('auth_token', data.data.auth_token);
                    }
                );
            },
            function (data) {
                return $q.reject(data);
            }
        );
    };

    authservice.register = function (data) {
        return $http.post(
            '/auth/register/',
            {'username': data.username, 'password': data.password, 'email': data.email}
        ).then(function (res) {
            MessageManager.toggleMessage('newAccount');
            return authservice.login(res.data.username, data.password);
        },
        function (error) {
            return $q.reject(error);
        });
    };

    authservice.changePassword = function (data) {
        return $http.post(
            '/auth/password/',
            {new_password: data.new_password1, re_new_password: data.new_password2, current_password: data.old_password}
        ).then(
            function (data) {
                MessageManager.toggleMessage('changePasswordSuccess');
            },
            function (error) {
                // djoser and django are using the same name, mapping need to be done manually
                var _data = _.cloneDeep(error.data);
                if (angular.isDefined(error.data.new_password)) {
                    _data.new_password1 = error.data.new_password;
                }
                if (angular.isDefined(error.data.re_new_password)) {
                    _data.new_password2 = error.data.re_new_password;
                }
                if (angular.isDefined(error.data.current_password)) {
                    _data.old_password = error.data.current_password;
                }
                error.data = _data;
                return $q.reject(error);
            }
        );
    };

    authservice.forgotPassword = function (data) {
        return $http.post(
            '/auth/password/reset/',
            {email: data.email}
        ).then(
            function (rep) {
                MessageManager.vars.emailSentResetPassword = data.email;
                MessageManager.toggleMessage('emailSentResetPassword');
            },
            function (error) {
                return $q.reject(error);
            }
        );
    };

    authservice.validate_token = function (token) {
        return authservice.login_with_token(token);
    };

    authservice.logout = function () {
        return $http.post('/auth/logout/').then(
            function () {
                authservice.logout_with_token();

                $rootScope.$emit('logout', {});
            }
        );
    };

    function auth_token_is_valid(auth_token) {
        return (angular.isDefined(auth_token) && auth_token !== null && auth_token !== 'null');
    }

    authservice.is_logged_in = function () {
        return auth_token_is_valid(authservice.auth_token);
    };

    /*
     Try to restore the auth token and user_info from localStorage
    */
    var stored_token = $window.localStorage.getItem('auth_token');
    if (auth_token_is_valid(stored_token)) {
        authservice.login_with_token(stored_token);
    }

    return authservice;
}
AuthenticationService.$inject = ['$http', '$window', '$q', '$rootScope', 'MessageManager'];
