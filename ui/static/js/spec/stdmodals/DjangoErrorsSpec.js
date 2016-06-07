describe('DjangoErrors service', function () {
    beforeEach(module('stdmodals'));

    beforeEach(function () {
        module(function ($provide) {
            $provide.value('djangoForm', jasmine.createSpyObj('djangoForm', ['setErrors']));
        });
    });

    beforeEach(inject(function (_DjangoErrors_, _djangoForm_) {
        DjangoErrors = _DjangoErrors_;
        djangoForm = _djangoForm_;
    }));

    it('should handle errors', function () {
        var form_scope = 'some_form_scope';
        var error = {data: {}};

        DjangoErrors.handle_errors(form_scope, error);

        expect(djangoForm.setErrors).toHaveBeenCalledWith(form_scope, {});
    });

    it('should display "Unexpected error" when error data is not an object', function () {
        var form_scope = 'some_form_scope';
        var error = {data: "Backend request failed"};

        DjangoErrors.handle_errors(form_scope, error);

        expect(djangoForm.setErrors).toHaveBeenCalledWith(form_scope, {'__all__': ['An unexpected error occured']});
    });

    it('should display "Unexpected error" when there is no error data', function () {
        var form_scope = 'some_form_scope';
        var error = {};

        DjangoErrors.handle_errors(form_scope, error);

        expect(djangoForm.setErrors).toHaveBeenCalledWith(form_scope, {'__all__': ['An unexpected error occured']});
    });


});