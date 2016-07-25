// Karma configuration
// Generated on Fri Jan 22 2016 18:52:01 GMT+0100 (CET)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: 'static_prod/',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
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

            'djng/js/django-angular.js',

            'stackframe/dist/stackframe.js',
            'error-stack-parser/dist/error-stack-parser.js',

            'sockjs-client/dist/sockjs-1.0.3.js',
            'luna_websockets/js/angular/module.js',

            /* These regexes are quite weird, but anything more generic throws "Weird Error" */
            'js/angular-app/**/module.js',
            'js/angular-app/**/resources.js',
            'js/angular-app/**/filters.js',
            'js/angular-app/**/services.js',
            'js/angular-app/**/controllers.js',
            'js/angular-app/dispatch.js',

            'angular-mocks/angular-mocks.js',
            'js/spec/**/*Spec.js'

    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
            'js/angular-app/**/module.js': ['coverage'],
            'js/angular-app/**/resources.js': ['coverage'],
            'js/angular-app/**/filters.js': ['coverage'],
            'js/angular-app/**/services.js': ['coverage'],
            'js/angular-app/**/controllers.js': ['coverage'],
            'js/angular-app/dispatch.js': ['coverage']
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage', 'junit'],

    // Configure coverage reports
    coverageReporter: {
      type : 'html',
      dir : '../jscoverage/'
    },

    // Configure junit reports
    junitReporter: {
      outputDir: '../karma_reports/'
    },

    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,

    client: {
      captureConsole: true
    },


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Chrome_without_sandbox', 'Firefox'],

      customLaunchers: {
        Chrome_without_sandbox: {
            base: 'Chrome',
                flags: ['--no-sandbox']
        }
    },

    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false,

    // Concurrency level
    // how many browser should be started simultaneous
    concurrency: Infinity
  })
}
