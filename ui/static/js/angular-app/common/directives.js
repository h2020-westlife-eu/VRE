angular.module('common')
    .directive('clickFunction', clickFunction)
    .directive('submitFunction', submitFunction);


/**
 * A ng-click alternative, optimized for buttons. The syntax is the same as for ng-click.
 * When triggered, the directive will replace the button text with a spinner, and prevent any further clicks on the
 * button until the promise has resolved.
 * The function passed to clickFunction should return a promise, and the directive will lock the button until the
 * promise is resolved.
 * For backwards compatibility, the directive supports functions that don't return a promise. In this case, it
 * behaves just like ng-click.
 * @type {string[]}
 */
clickFunction.$inject = ['$parse', '$q'];
function clickFunction($parse, $q) {
    return {
        restrict: 'A',
        compile: function ($element, attr) {
            var fn = $parse(attr.clickFunction);
            return function ngEventHandler(scope, element) {
                var handler = function (event) {
                    // If element is disabled, ignore the event. The browser shouldn't even send us the event, but
                    // it can happen if the user mashes the button (Coucou François)
                    if (element.hasClass('disabled')) {
                        return;
                    }

                    var loading_text = '<i class="fa fa-spinner fa-spin"></i> Processing...';
                    var old_text = element.html();
                    element.addClass('disabled');
                    element.html(loading_text);


                    var callback = function () {
                        return fn(scope, {$event: event});
                    };
                    $q.when(scope.$apply(callback)).finally(function() {
                        element.html(old_text);
                        element.removeClass('disabled');
                    });
                };
                element.on('click', handler);
            };
        }
    };
}


/**
 * This directive, to be added to a form, reacts to the "submit" event (form submission by clicking on submit or with
 * the Enter key.
 * When triggered, it will look for the button in the form that has the class "submit_button" (or the button in the
 * form, if there is only one), and click on it. From then on, it behaves exactly as if there was a click-function
 * directive on that button.
 * The value of the directive is used in the same way as the value for click-function.
 * This directive *replaces* click-function. Don't use both in the same form.
 * @param $parse
 * @param $q
 * @returns {{restrict: string, compile: compile}}
 */
function submitFunction($parse, $q) {
    return {
        restrict: 'A',
        compile: function ($element, attr) {
            var fn = $parse(attr.submitFunction);
            return function ngEventHandler(scope, element) {
                var handler = function (event) {
                    var button_elements = element.find('button');
                    var button_element;

                    if (button_elements.length === 0) {
                        return;
                    } else if (button_elements.length === 1) {
                        button_element = angular.element(button_elements[0]);
                    } else {
                        button_element = _.find(
                            button_elements,
                            function(elt) {
                                return angular.element(elt).hasClass('submit_button');
                            }
                        );

                        if (angular.isUndefined(button_element)) {
                            return;
                        }

                        button_element = angular.element(button_element);
                    }

                    // If element is disabled, ignore the event. The browser shouldn't even send us the event, but
                    // it can happen if the user mashes the button (Coucou François)
                    if (button_element.hasClass('disabled')) {
                        return;
                    }

                    var loading_text = '<i class="fa fa-spinner fa-spin"></i> Processing...';
                    var old_text = button_element.html();
                    button_element.addClass('disabled');
                    button_element.html(loading_text);


                    var callback = function () {
                        return fn(scope, {$event: event});
                    };
                    $q.when(scope.$apply(callback)).finally(function() {
                        button_element.html(old_text);
                        button_element.removeClass('disabled');
                    });

                };
                element.on('submit', handler);
            };
        }
    };
}
submitFunction.$inject = ['$parse', '$q'];
