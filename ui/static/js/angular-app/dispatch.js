angular.module('dispatch', ['ng', 'ngRoute', 'ngAnimate', 'settings', 'common', 'intercom', 'pype.datasets', 'auth', 'loggingModule', 'luna_websockets', 'pype.jobportals'])

    /*
     Redirect to login page whenever an API call returns 401 (which means the provided a bad auth token
     */
    .config(['$httpProvider',
        function ($httpProvider) {
            $httpProvider.interceptors.push(
                ['$q', '$location',
                    function ($q, $location) {
                        return {
                            'responseError': function (rejection) {
                                if (rejection.status === 401) {
                                    console.log('Got 401. Redirecting to /login');
                                    $window.location('/login/');
                                }
                                return $q.reject(rejection);
                            }
                        };
                    }
                    ]
            );
        }]
        )

    /*
     Define all the routes
     */
    .config(['$routeProvider',
        function ($routeProvider) {
            $routeProvider
                .when('/main', {
                    templateUrl: 'explorer.html',
                    controller: 'ExplorerController'
                })
                .when('/datasets', {
                    templateUrl: 'datasets.html',
                    controller: 'DatasetsController',
                    resolve: {
                        pk: function () { return undefined; }
                    }
                })
                /*
                .when('/dataset/:datasetId', {
                    templateUrl: 'datasets.html',
                    controller: 'DatasetsController',
                    resolve: {
                        pk: ['$route', function ($route) { return parseInt($route.current.params.datasetId, 10); }]
                    }
                })
                */
                /*
                .when('/datafile/create/:datasetId', {
                    templateUrl: 'datafile_form.html',
                    controller: 'DatafileCreateController'
                })
                */
                .when('/storage_providers', {
                    templateUrl: 'storage_providers.html',
                    controller: 'StorageProvidersController',
                    resolve: {
                        'StorageProviderManager': ['StorageProviderManager', function (StorageProviderManager) { return StorageProviderManager.load(); }]
                    }
                })
                .when('/action_log', {
                    templateUrl: 'action_log.html',
                    controller: 'UserActionController'
                })
                .when('/login', {
                    templateUrl: 'login.html',
                    controller: 'LoginController'
                })
                .when('/logout', {
                    templateUrl: 'logout.html',
                    controller: 'LogoutController'
                })
                .when('/profile', {
                    templateUrl: 'profile.html',
                    controller: 'ProfileController as profileCtrl',
                    resolve: {
                        'AuthenticationService': ['AuthenticationService', function (AuthenticationService) { return AuthenticationService.waitForLoad(); }]
                    }
                })
                .when('/register', {
                    controller: 'RegisterController',
                    templateUrl: 'register.html'
                })
                .when('/forgot_password', {
                    controller: 'ForgotPasswordController',
                    templateUrl: 'forgot_password.html'
                })
                .when('/password/reset/:token/:uid/', {
                    templateUrl: 'reset_password.html',
                    controller: 'ResetPasswordController'
                })
                .when('/jobs', {
                    templateUrl: 'jobs.html',
                    controller: 'JobsController'
                })
                .when('/jobsportals', {
                    templateUrl: 'job_portals.html',
                    controller: 'ExploreJobPortalsController'
                })
                .otherwise({
                    // CAUTION: redirectTo doesn't fire $routeChangeStart, and so isn't affected by our catch-all redirection
                    redirectTo: '/main'
                });

//                $locationProvider.html5Mode(true);
        }]
        )

    /*
     This redirects the user to the login page if he isn't logged in
     */
    .run(['$rootScope', '$location', 'AuthenticationService', 'IntercomService',
        function ($rootScope, $location, AuthenticationService, IntercomService) {
            var whitelisted_controllers = [
                'LoginController',
                'RegisterController',
                'ForgotPasswordController',
                'ResetPasswordController'
            ];

            $rootScope.$on('$routeChangeStart', function (event, next, current) {
                // console.log('Trying to change to', next.controller);
                if (!AuthenticationService.is_logged_in()) {
                    // If the controller isn't whitelisted, force redirect to login page
                    if (whitelisted_controllers.indexOf(next.controller) === -1) {
                        $location.path('/login');
                        event.preventDefault();
                    }
                } else {
                    if (next.controller === 'LoginController') {
                        $location.path('/main');
                        event.preventDefault();
                    }
                }
            });

            $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
                $rootScope.activeTab = current.controller;

                IntercomService.update();
            });
        }]
        )

    /* Disable animations */
    .run(['$animate', function ($animate) {
        $animate.enabled(false);
    }])

    /* Set some global variables */
    .run(['$rootScope',
        function ($rootScope) {
            "use strict";
            $rootScope.left_panel_width = 300;
        }]
        )


    .run(['LunaWebsocketsService', 'AppSettingsService', function(LunaWebsocketsService, AppSettingsService) {
        "use strict";

        if (AppSettingsService.DEBUG) {
            // Example/Debug code, to show how to use LunaWebsocketsService
            LunaWebsocketsService.subscribe('console.msg', function (msg, topic) {
                console.log('Caught message on topic console.msg:', msg);
            });
            LunaWebsocketsService.subscribe('*', function (msg, topic) {
                console.log('Catchall caught a message on topic', topic, ':', msg);
            });
        }
    }]);
