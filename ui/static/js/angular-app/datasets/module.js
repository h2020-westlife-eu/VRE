angular.module('pype.datasets', [
    'stdmodals',
    'ngResource',
    'ngAnimate',
    'ngCookies',
    'ngRoute',
    'ui.bootstrap',
    'ng.django.forms',
//  'loggingModule',
//  'ng.django.urls',  // url management by django-angular
    'ngFileUpload'
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
