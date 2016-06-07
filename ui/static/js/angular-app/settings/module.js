angular.module('settings', [])
    .factory('AppSettingsService', AppSettingsService);

/**
 * A service that exposes anything is present in the django configuration for the settings JS_CONFIG. This is
 * usually a config dict
 * Note: The {% js_config %} tag must be present somewhere in the HTML template
 * @constructor
 */
function AppSettingsService($document) {
    "use strict";

    return JSON.parse(angular.element($document[0].querySelector('#js_config')).html());

}
AppSettingsService.$inject = ['$document'];