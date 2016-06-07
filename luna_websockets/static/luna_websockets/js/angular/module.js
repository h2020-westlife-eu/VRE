angular.module('luna_websockets', [])
    .factory('LunaWebsocketsService', LunaWebsocketsService);

/**
 * A service that connects to a websocket and listens for messages
 * @constructor
 */
function LunaWebsocketsService($rootScope, $timeout, AuthenticationService, AppSettingsService) {
    "use strict";

    var WsServiceImpl = function () {
        var that = this;

        var callbacks = {};

        $rootScope.$on('login', function () {
            var reconnectTimeout = null;
            var conn = null;
            var retrying = false;

            var setup_conn = function () {
                conn = new SockJS(AppSettingsService.WS_SERVER);

                conn.onopen = function () {
                    if (retrying) {
                        console.log('Reconnection succeeded');
                        retrying = false;
                    }
                    conn.send(angular.toJson({cmd: 'AUTH', token: AuthenticationService.auth_token}));

                    $rootScope.$on('logout', function () {
                        conn.send(angular.toJson({cmd: 'DEAUTH'}));
                        callbacks = {};  // Remove all callbacks on logout
                        conn.onclose = undefined;  // Disable the reconnect logic
                        conn.close();
                    });
                };

                conn.onmessage = function (e) {
                    var msg = angular.fromJson(e.data);
                    var hasCalled = false;
                    if (angular.isDefined(callbacks[msg.topic])) {
                        _.each(callbacks[msg.topic], function (cb) {
                            return cb(msg.data, msg.topic);
                        });
                        if (callbacks[msg.topic].length > 0) {
                            hasCalled = true;
                        }
                    }
                    if (angular.isDefined(callbacks['*'])) {
                        _.each(callbacks['*'], function (cb) {
                            return cb(msg.data, msg.topic);
                        });
                        if (callbacks['*'].length > 0) {
                            hasCalled = true;
                        }
                    }
                    if (hasCalled) {
                        $rootScope.$apply();
                    }
                };

                conn.onclose = function () {
                    conn = null;
                    retrying = true;
                    reconnectTimeout = $timeout(function () {
                        console.log('Websockets connection lost. Trying to reconnect...');
                        setup_conn();
                    }, 2000);
                };
            };
            setup_conn();

        });


        /**
         * Registers a callback function, to be fired when a message is received on a specific topic
         * If the function has already been registered, this is a no-op
         * @param topic the topic on which to listen, or '*' to listen for all messages
         * @param callback a callback function, with signature callback(message_data, topic)
         */
        that.subscribe = function (topic, callback) {
            if (angular.isUndefined(callbacks[topic])) {
                callbacks[topic] = [];
            }
            if (_.includes(callbacks[topic], callback)) {
                return;
            }
            callbacks[topic].push(callback);
        };

        /**
         * Unregisters a callback function from a given topic
         * @param topic the topic where the function had been registered
         * @param callback the callback function that you want to remove
         */
        that.unsubscribe = function (topic, callback) {
            if (angular.isUndefined(callbacks[topic])) {
                return;
            }
            _.remove(callbacks[topic], function (d) { return d === callback; });
        };

    };

    return new WsServiceImpl();

}
LunaWebsocketsService.$inject = ['$rootScope', '$timeout', 'AuthenticationService', 'AppSettingsService'];
