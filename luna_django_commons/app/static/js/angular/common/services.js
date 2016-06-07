angular.module('common')
    .factory('MessageManager', MessageManager);

function MessageManager($timeout) {
    "use strict";
    var ServiceMessageManager = function () {
        var self = this;

        self.messages = {};
        self.vars = {};

        self.toggleMessage = function (key) {
            if (angular.isUndefined(self.messages[key])) {
                self.messages[key] = false;
            }
            self.messages[key] = !self.messages[key];
            $timeout(function () {
                self.messages[key] = !self.messages[key];
            }, 3000);
        };
    };

    var dm = new ServiceMessageManager();
    return dm;
}
MessageManager.$inject = ['$timeout'];