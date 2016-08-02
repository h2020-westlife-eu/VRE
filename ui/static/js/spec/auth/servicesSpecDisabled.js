describe('AuthenticationService service', function () {
    beforeEach(module('auth'));

    // We need to mock $window in order to mock local storage
    // Otherwise, the content of localstorage is preserve between runs
    beforeEach(function () {
        windowMock = {
            localStorage: {},
            location: {}
        };
        windowMock.localStorage.getItem = function (key) {
            if (windowMock.localStorage.hasOwnProperty(key)) {
                return windowMock.localStorage[key];
            } else {
                return null;
            }
        };
        windowMock.localStorage.setItem = function (key, value) {
            windowMock.localStorage[key] = value;
        };
        windowMock.location.reload = jasmine.createSpy('reload');

        module(function ($provide) {
            $provide.value('$window', windowMock);
        });
    });

    beforeEach(inject(function (AuthenticationService, _$httpBackend_) {
        service = AuthenticationService;
        $httpBackend = _$httpBackend_;
    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    it('should allow the user to register', function () {
        var data = {
            username: 'a_user',
            password: 'a_user_password',
            email: 'a_user@example.com'
        };

        $httpBackend.expectPOST(
            '/auth/register/',
            {
                'username': 'a_user',
                'password': 'a_user_password',
                'email': 'a_user@example.com'
            }
        ).respond(201, {'username': 'a_user', 'email': 'a_user@example.com'});

        $httpBackend.expectPOST(
            '/auth/login/',
            {
                'username': 'a_user',
                'password': 'a_user_password'
            }
        ).respond(200, {'auth_token': 'a_token'});

        $httpBackend.expectGET(
            '/auth/me/'
        ).respond(
            200,
            {
                'id': 1,
                'username': 'a_user',
                'email': 'a_user@example.com'
            }
        );

        service.register(data);
        $httpBackend.flush();

        expect(service.auth_token).toEqual('a_token');
        expect(service.user_info).toEqual({
            'id': 1,
            'username': 'a_user',
            'email': 'a_user@example.com',
            'created_at': 0
        });
        expect(service.is_logged_in()).toEqual(true);

    });

    it('should handle register failures', function () {
        $httpBackend.expectPOST(
            '/auth/register/',
            {
                'username': 'a_user',
                'email': 'a_user@example.com'
            }
        ).respond(400, {"password": ["This field is required."]});

        service.register({
            'username': 'a_user',
            'email': 'a_user@example.com'
        });
        $httpBackend.flush();
    });

    it('should allow the user to login', function () {
        $httpBackend.expectPOST(
            '/auth/login/',
            {
                'username': 'a_user',
                'password': 'a_user_password'
            }
        ).respond(200, {'auth_token': 'a_token'});

        $httpBackend.expectGET(
            '/auth/me/'
        ).respond(
            200,
            {
                'id': 1,
                'username': 'a_user',
                'email': 'a_user@example.com'
            }
        );

        service.login('a_user', 'a_user_password');
        $httpBackend.flush();

        expect(service.auth_token).toEqual('a_token');
        expect(service.user_info).toEqual({
            'id': 1,
            'username': 'a_user',
            'email': 'a_user@example.com',
            'created_at': 0
        });
        expect(service.is_logged_in()).toEqual(true);

    });

    it('should handle when login fails', function () {
        $httpBackend.expectPOST(
            '/auth/login/',
            {
                'username': 'a_user',
                'password': 'a_user_password'
            }
        ).respond(400, {'__all__': ["Unable to login with provided credentials."]});

        service.login('a_user', 'a_user_password');
        $httpBackend.flush();

        expect(service.auth_token).toEqual(undefined);
        expect(service.user_info).toEqual(undefined);
        expect(service.is_logged_in()).toEqual(false);

    });

    it('should handle reauthentication failures', function () {
        $httpBackend.expectGET(
            '/auth/me/'
        ).respond(401, {"detail":"Invalid token."});

        service.login_with_token('fwah');
        $httpBackend.flush();

        expect(service.auth_token).toEqual(undefined);
        expect(service.user_info).toEqual(undefined);
        expect(service.is_logged_in()).toEqual(false);
        expect(windowMock.location.reload).toHaveBeenCalled();
    });

    it('should handle validate_token()', function () {
        $httpBackend.expectGET(
            '/auth/me/'
        ).respond(
            200,
            {
                'id': 1,
                'username': 'a_user',
                'email': 'a_user@example.com'
            }
        );

        service.validate_token('fwah');
        $httpBackend.flush();

        expect(service.auth_token).toEqual('fwah');
        expect(service.user_info).toEqual({
            'id': 1,
            'username': 'a_user',
            'email': 'a_user@example.com',
            'created_at': 0
        });
        expect(service.is_logged_in()).toEqual(true);
    });

    it('should allow the user to logout', function () {
        $httpBackend.expectPOST(
            '/auth/logout/'
        ).respond(200);

        service.logout();
        $httpBackend.flush();
        expect(service.auth_token).toEqual(undefined);
        expect(service.user_info).toEqual(undefined);
        expect(service.is_logged_in()).toEqual(false);
        expect(windowMock.location.reload).toHaveBeenCalled();
    });

    it('should allow the user to request an email to change password', function () {
        $httpBackend.expectPOST(
            '/auth/password/reset/',
            {
                'email': 'a_user@example.com'
            }
        ).respond(200);

        service.forgotPassword({'email': 'a_user@example.com'});
        $httpBackend.flush();
    });

    it('should handle errors on requesting a password change', function () {
        $httpBackend.expectPOST(
            '/auth/password/reset/',
            {
                'email': 'a_user@example.com'
            }
        ).respond(500, 'UNEXPECTED FAILURE EVERYTHING IS BROKEN RUN FOR YOUR LIFE THE MACHINE WANTS TO KILL US A*scrounch*')
        service.forgotPassword({'email': 'a_user@example.com'});
        $httpBackend.flush();
    });

});