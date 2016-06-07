angular
    .module('loggingModule', ['common'])

    .factory('traceService', function () {
        return ({
            print: function (arg) {
                "use strict";
                var exc = arg;
                return _.map(ErrorStackParser.parse(exc), function (v) {
                    return v.toString();
                }).join('\n');
            }
        });
    })

    .provider("$exceptionHandler", {
        $get: ['exceptionLoggingService', function (exceptionLoggingService) {
            return exceptionLoggingService;
        }]
    })

    .factory("exceptionLoggingService",
        ["$log", "$window", "traceService", "AppSettingsService",
            function ($log, $window, traceService, AppSettingsService) {
                function error(exception, cause) {
                    // Pass-through to the default log-to-console behaviour
                    $log.error.apply($log, arguments);

                    if (!AppSettingsService.DEBUG) {
                        try {
                            var errorMessage = exception.message;

                            var stackTrace = traceService.print(exception);

                            var data = {
                                url: $window.location.href,
                                message: errorMessage,
                                type: "exception",
                                stackTrace: stackTrace,
                                cause: (cause || "")
                            };

                            // Use XHR and not $http
                            var xhr = new XMLHttpRequest();

                            xhr.open('POST', 'https://seekscale.com:41002/event', true);
                            xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
                            xhr.send(angular.toJson(data));
                        } catch (loggingError) {
                            $log.warn('Error: Server-side logging failed');
                            $log.log(loggingError);
                        }
                    }
                }

                return error;
            }]);
