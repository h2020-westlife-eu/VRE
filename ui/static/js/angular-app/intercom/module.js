angular.module('intercom', [])
    .factory('IntercomService', IntercomService);

/**
 * Intercom.io integration
 * @param $rootScope
 * @param $window
 * @param AppSettingsService
 * @returns {IntercomServiceImpl}
 * @constructor
 */
function IntercomService($rootScope, $window, AppSettingsService) {
    "use strict";

    var IntercomServiceImpl = function () {
        var that = this;

        if (!AppSettingsService.DEBUG) {
            $window.Intercom('boot', {
                app_id: AppSettingsService.INTERCOM_APP_ID
            });

            $rootScope.$on('login', function (e, data) {
                $window.Intercom('update', {
                    name: data.username,
                    user_id: data.id,
                    email: data.email,
                    created_at: data.created_at
                });
            });

            $rootScope.$on('logout', function () {
                $window.Intercom('shutdown');
            });
        }

        that.update = function () {
            if (!AppSettingsService.DEBUG) {
                $window.Intercom('update');
            }
        };

        that.trackEvent = function (event, data) {
            if (!AppSettingsService.DEBUG) {
                $window.Intercom('trackEvent', event, data);
            }
        };
    };
    return new IntercomServiceImpl();


}
IntercomService.$inject = ['$rootScope', '$window', 'AppSettingsService'];