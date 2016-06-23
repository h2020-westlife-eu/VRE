angular.module('pype.jobportals', [
    'stdmodals',
    'ngResource',
    'ngAnimate',
    'ngCookies',
    'ngRoute',
    'ui.bootstrap',
    'djng.forms',
//  'loggingModule',
    'ngFileUpload',
    'pype.datasets'
])

    .config(['$httpProvider', function ($httpProvider) {
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }])

    .config(['$resourceProvider', function ($resourceProvider) {
        // Don't strip trailing slashes from calculated URLs
        $resourceProvider.defaults.stripTrailingSlashes = false;
    }])

    .run(['$http', '$cookies', function ($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    }]);
