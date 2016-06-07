describe('traceService service', function () {
    beforeEach(module('loggingModule'));

    beforeEach(function () {
        module(function ($provide) {
            //$provide.value('AppSettingsService', {});
            /*
            $provide.value('$httpBackend', {});
            $provide.value('$rootScope', {});
            $provide.value('$http', {});
            $provide.value('$exceptionHandler', {});
            */
        })
    });

    beforeEach(inject(function (_traceService_) {
        traceService = _traceService_;
    }));

    it('should serialize the exception', function () {
        try {
            throw new Error('Oops');
        } catch (e) {
            traceService.print(e);
        }
    });

});


describe('exceptionLoggingService service', function () {
    beforeEach(module('loggingModule'));

    describe('when DEBUG is false', function () {
        beforeEach(function () {
            module(function ($provide) {
                $provide.value('AppSettingsService', {'DEBUG': false});
            });
        });

        beforeEach(inject(function (_exceptionLoggingService_, _$log_) {
            exceptionLoggingService = _exceptionLoggingService_;
            $log = _$log_;
        }));

        it('should post an error', function () {
            var xhrObj = jasmine.createSpyObj('xhrObj', ['open', 'setRequestHeader', 'send']);
            var spy = spyOn(window, 'XMLHttpRequest');
            spy.and.returnValue(xhrObj);

            try {
                throw new Error('Oops');
            } catch (e) {
                exceptionLoggingService(e);
                expect(xhrObj.open).toHaveBeenCalled();
                expect(xhrObj.setRequestHeader).toHaveBeenCalled();
                expect(xhrObj.send).toHaveBeenCalled();
            }
        });

        it('should log something if logging failed', function() {
            spyOn(window, 'XMLHttpRequest').and.throwError('XMLHttpRequest() does not exist');

            try {
                throw new Error('Oops');
            } catch (e) {
                exceptionLoggingService(e);
                expect($log.warn.logs).toContain(['Error: Server-side logging failed']);
                expect($log.log.logs).toContain([new Error('XMLHttpRequest() does not exist')]);
            }

        });
    });

    describe('when DEBUG is true', function () {
        beforeEach(function () {
            module(function ($provide) {
                $provide.value('AppSettingsService', {'DEBUG': true});
            });
        });

        beforeEach(inject(function (_exceptionLoggingService_) {
            exceptionLoggingService = _exceptionLoggingService_;
        }));

        it('should not post an error', function () {
            AppSettingsService.DEBUG = true;

            var xhrObj = jasmine.createSpyObj('xhrObj', ['open', 'setRequestHeader', 'send']);
            var spy = spyOn(window, 'XMLHttpRequest');
            spy.and.returnValue(xhrObj);

            try {
                throw new Error('Oops');
            } catch (e) {
                exceptionLoggingService(e);
                expect(xhrObj.open).not.toHaveBeenCalled();
                expect(xhrObj.setRequestHeader).not.toHaveBeenCalled();
                expect(xhrObj.send).not.toHaveBeenCalled();
            }
        });
    });

});
