from django_assets import Bundle, register

# Assets for the landing pages
css_landing = Bundle(
    'bootstrap/dist/css/bootstrap.css',
    'css/landing-page.css',

    filters=('cssrewrite', 'yui_css',),
    output='compiled-assets/gen/css_landing.%(version)s.css'
)

register('css_landing', css_landing)

js_landing = Bundle(
    'jquery/dist/jquery.js',
    'bootstrap/dist/js/bootstrap.js',

    filters='closure_js',
    output='compiled-assets/gen/js_landing.%(version)s.js')

register('js_landing', js_landing)


# Assets for the application
css_main = Bundle(
    'bootstrap/dist/css/bootstrap.css',
    'djangular/css/styles.css',
    'font-awesome/css/font-awesome.css',

    'css/datasets.css',

    filters=('cssrewrite', 'yui_css',),
    output='compiled-assets/gen/css_main.%(version)s.css'
)

register('css_main', css_main)

js_main = Bundle(
    'jquery/dist/jquery.js',
    'lodash/lodash.js',
    'angular/angular.js',
    'angular-bootstrap/ui-bootstrap-tpls.js',
    'angular-route/angular-route.js',
    'angular-resource/angular-resource.js',
    'angular-cookies/angular-cookies.js',
    'angular-animate/angular-animate.js',
    'angular-messages/angular-messages.js',
    'ng-file-upload/ng-file-upload.js',

    'moment/min/moment-with-locales.js',

    'djangular/js/django-angular.js',

    'stackframe/dist/stackframe.js',
    'error-stack-parser/dist/error-stack-parser.js',

    'sockjs-client/dist/sockjs-1.0.3.js',
    'luna_websockets/js/angular/module.js',

    'js/angular-app/datasets/module.js',
    'js/angular-app/datasets/resources.js',
    'js/angular-app/datasets/controllers.js',
    'js/angular-app/datasets/services.js',
    'js/angular-app/datasets/filters.js',
    'js/angular-app/auth/module.js',
    'js/angular-app/auth/services.js',
    'js/angular-app/auth/controllers.js',
    'js/angular-app/common/module.js',
    'js/angular-app/common/directives.js',
    'js/angular-app/common/services.js',
    'js/angular-app/intercom/module.js',
    'js/angular-app/settings/module.js',
    'js/angular-app/logging/module.js',
    'js/angular-app/stdmodals/module.js',
    'js/angular-app/stdmodals/controllers.js',
    'js/angular-app/stdmodals/services.js',
    'js/angular-app/jobportals/module.js',
    'js/angular-app/jobportals/controllers.js',
    'js/angular-app/dispatch.js',

    filters='closure_js',
    output='compiled-assets/gen/js_main.%(version)s.js')

register('js_main', js_main)
