# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>

import argparse
from copy import deepcopy
import datetime
import json
import os
import pwd
import re
import shlex
import shutil
import subprocess
import time
import traceback

import yaml


# Prevents things to fail on linux because WindowsError isn't defined there.
# Trick stolen from shutil.
try:
    WindowsError
except NameError:
    WindowsError = None


PYPI_MIRROR_HOST = '10.63.90.56'
PYPI_URL = 'http://10.63.90.56:31000/luna/prod/+simple/'

PYPI_SUBMIT_URL = 'http://10.63.90.56:30000/pypi/'
HOME = os.path.expanduser('~')


###
# Helpers
###
def _pip_exec(pip_args, get_output=False):
    pip_cmd = ['/usr/bin/env', 'pip'] + pip_args

    return _exec(pip_cmd, get_output=get_output)


def _exec(command, get_output=False, silent_errors=False):
    print("+ %s" % command)

    try:
        # We set universal_newlines so that we get a str (and not a byte string) in return
        s = datetime.datetime.utcnow()
        r = subprocess.check_output(command, universal_newlines=True)
        elapsed_time = (datetime.datetime.utcnow() - s).total_seconds()
    except subprocess.CalledProcessError as e:
        if not silent_errors:
            print('>> Command execution failed. Output:')
            print(e.output)
        raise
    else:
        print("-> %.2fs" % elapsed_time)
        if get_output:
            return r
        else:
            return None


def _argparse_function(subparsers, call_function, command_name, description, arguments=None):
    f_parser = subparsers.add_parser(
        command_name,
        help=description,
        description=description,
    )

    if arguments is not None:
        for argument in arguments:
            f_parser.add_argument(**argument)

    f_parser.set_defaults(func=call_function)

    return f_parser


def start_postgresql():
    print("Starting postgresql...")
    _exec([
        'sudo',
        '/usr/sbin/service',
        'postgresql',
        'start',
    ])


def wait_for_postgresql():
    print("Waiting for postgresql server to be ready...")

    i = 0
    ready = False
    while i < 60:
        try:
            _exec([
                'sudo',
                '/usr/bin/pg_isready',
            ], silent_errors=True)
            ready = True
            break
        except subprocess.CalledProcessError:
            i += 1
            time.sleep(5)

    if not ready:
        raise RuntimeError('Postgresql did not start in time. Aborting...')


def start_redis():
    print("Starting redis...")
    _exec([
        'sudo',
        '/usr/bin/service',
        'redis-server',
        'start',
    ])


def setup_pypi_mirror():
    with open(os.path.join(HOME, '.pydistutils.cfg'), 'w') as fh:
        fh.write("""[easy_install]
index_url = """ + PYPI_URL + """
""")

    try:
        os.makedirs(os.path.join(HOME, '.pip'))
    except Exception:
        pass

    with open(os.path.join(HOME, '.pip', 'pip.conf'), 'w') as fh:
        fh.write("""[global]
index-url = """ + PYPI_URL + """
trusted-host = """ + PYPI_MIRROR_HOST + """
""")

    with open(os.path.join(HOME, '.pypirc'), 'w') as fh:
        fh.write("""[distutils]
index-servers =
    luna_internal
    devpi_luna

[luna_internal]
username:foo
password:bar
repository:""" + PYPI_SUBMIT_URL + """

[devpi_luna]
username:luna
password:bHdTzu1gPYcxbtEoq3MiwdKeR
repository:http://10.63.90.56:31000/luna/prod/
""")


def setup_venv(pyenv_path):
    try:
        shutil.rmtree(pyenv_path)
    except Exception:
        pass

    _exec([
        '/usr/bin/env',
        'virtualenv',
        '--no-site-packages',
        pyenv_path
    ])


def setup_venv_py3(pyenv_path):
    try:
        shutil.rmtree(pyenv_path)
    except Exception:
        pass

    _exec([
        '/usr/bin/env',
        'pyvenv-3.4',
        pyenv_path
    ])


def _expand_package_specs(package_specs):
    # Expand requirements file, if any, and check for ignored packages
    ignored_packages=['pkg-resources']
    try:
        idx = package_specs.index('-r')
        requirements_file = package_specs[idx+1]
        package_specs = package_specs[:idx] + package_specs[idx+2:]
        with open(requirements_file, 'r') as fh:
            requirements_data = fh.read()
        requirements_lines = requirements_data.splitlines()
        for requirement_line in requirements_lines:
            requirement_line = requirement_line.strip()  # Remove whitespace
            if requirement_line.startswith('#'):
                continue
            if len(requirement_line) == 0:
                continue
            requirement_line_parts = requirement_line.split('==')
            if requirement_line_parts[0] in ignored_packages:
                continue
            else:
                package_specs.append(requirement_line)
    except ValueError:
        pass

    return package_specs


def build_wheel_cache(wheels_path, package_specs):
    package_specs = _expand_package_specs(package_specs)

    _pip_exec(['install', 'wheel'])
    _pip_exec(['wheel', '--wheel-dir=%s' % wheels_path, '--find-links=%s' % wheels_path] + package_specs)
    _pip_exec(['install', '--use-wheel', '--no-index', '--find-links=%s' % wheels_path] + package_specs)


def install_from_wheel_cache(wheels_path, package_specs):
    package_specs = _expand_package_specs(package_specs)
    _pip_exec(['install', 'wheel'])
    _pip_exec(['install', '--use-wheel', '--no-index', '--find-links=%s' % wheels_path] + package_specs)


def upgrade_pip():
    _pip_exec(['install', '--upgrade', 'pip'])


def create_build_info(version=None):
    data = {}

    # Git revision
    try:
        git_revision = _exec([
            '/usr/bin/env',
            'git',
            'rev-parse',
            '--verify',
            '-q',
            'HEAD'
        ], get_output=True, silent_errors=True).strip()
    except:
        traceback.print_exc()
        git_revision = None
    data['git_revision'] = git_revision

    # Build number
    data['build_number'] = os.environ.get('BUILD_NUMBER')

    # Build version
    data['version'] = version

    # Pypi packages
    try:
        output = _pip_exec(['freeze'], get_output=True)
        deps = {}
        for line in output.splitlines():
            pkg, version = line.split('==')
            deps[pkg] = version
        data['pypi_deps'] = deps
    except:
        traceback.print_exc()

    # Dump the data to disk
    with open('build_info.txt', 'w') as fh:
        fh.write(json.dumps(data, indent=4))


def freeze_requirements():
    output = _pip_exec(['freeze'], get_output=True)
    return output


def _create_dir(path):
    """Ensure a directory exists. Creates it otherwise.
    This catches all sorts of "Directory already exist" exceptions,
    and lets the others pass through unchanged."""
    try:
        os.makedirs(path)
    except IOError as e:
        if e.errno == 17:
            # Already exists. Ok for us.
            pass
        else:
            raise e
    except WindowsError as e:
        if e.winerror == 183:
            # Already exists
            pass
        elif e.winerror == 5:
            # Access denied.
            # We get this error when we do os.makedirs("C:\\") (it does *not* happen for "C:")
            # No idea why, but fixing it anyway.
            # We get the error whether the drive exists or not, so we need to test that ourselves
            drive, subpath = os.path.splitdrive(path)
            if subpath == "\\" and os.path.exists(drive):
                pass
            else:
                raise e
        else:
            raise e
    except OSError as e:
        if e.errno == 17:
            # Already exists. Ok for us.
            pass
        else:
            raise e


def _gen_archive(output_name, exclude_paths, version=None):
    tar_cmd = [
        '/usr/bin/env',
        'tar',
    ]

    _create_dir('.build')

    for path in exclude_paths + ['.build']:
        tar_cmd.append("--exclude=./%s" % path)

    if version is not None:
        output_filename = '%s.%s.tar.xz' % (output_name, version)
    else:
        output_filename = '%s.tar.xz' % output_name

    tar_cmd += ['-Jcf', '.build/%s' % output_filename, '.']

    _exec(tar_cmd)


def _extract_django_module_from_manage_py():
    with open('manage.py', 'r') as fh:
        data = fh.read()

    m = re.search(r'os.environ.setdefault\("DJANGO_SETTINGS_MODULE", "(?P<module>\w+).settings"\)', data)

    if m is not None:
        return m.groupdict()['module']
    else:
        return None


def _make_supervisor_environment_string(env):
    return ','.join([
        "%s=\"%s\"" % (k, env[k]) for k in env.keys()
    ])


def load_config(source_dir=None):
    if source_dir is None:
        source_dir = os.getcwd()
    candidate_paths = ['maho.yml', 'deploy/maho.yml']
    full_candidate_paths = [os.path.join(source_dir, p) for p in candidate_paths]

    config_path = None
    for candidate_config_path in full_candidate_paths:
        if os.path.exists(candidate_config_path):
            config_path = candidate_config_path
            break

    if config_path is None:
        raise RuntimeError('Could not find maho.yml!')

    with open(config_path, 'r') as fh:
        config = yaml.load(fh.read())

    default_conf = {
        'project': 'UNNAMED_PROJECT',
        'env': {},
        'python_version': 'python3',
        'modules': [],
        'test_commands': [],

        'uwsgi_apps': [],
        'daemon_commands': []
    }
    default_conf.update(config)

    return default_conf


def load_deployment_config():
    candidate_paths = ['deploy.yml']

    config_path = None
    for candidate_config_path in candidate_paths:
        if os.path.exists(candidate_config_path):
            config_path = candidate_config_path
            break

    if config_path is None:
        raise RuntimeError('Could not find deploy.yml!')

    with open(config_path, 'r') as fh:
        config = yaml.load(fh.read())

    default_conf = {
        'deployment_name': 'UNNAMED_DEPLOYMENT',
        'listen_port': None,
        'env': {},
        'additional_files': {}
    }
    default_conf.update(config)

    return default_conf


def cache_dependencies(args):
    config = load_config()

    if os.path.exists('requirements.txt'):
        pyenv_path = '.pyenv'
        wheels_dir = 'py_wheels'

        setup_pypi_mirror()
        if config['python_version'] == 'python3':
            setup_venv_py3(pyenv_path)
        else:
            setup_venv(pyenv_path)
        os.environ['PATH'] = os.path.join(pyenv_path, 'bin') + os.pathsep + os.environ['PATH']
        upgrade_pip()
        build_wheel_cache(wheels_dir, ['-r', 'requirements.txt'])


###
# The main build command
###
def build(args):
    #
    # Things that we can't guess:
    # project name
    # requires postgresql
    # requires redis
    # DJANGO_MODE/DJANGO_SETTINGS_MODULE
    # python2 vs python3

    config = load_config()

    ###
    # Environment
    ###
    env = {
        'LANG': 'en_us.UTF-8',
        'LANGUAGE': 'en_US:en',
        'LC_ALL': 'en_US.UTF-8',
    }
    os.environ.update(env)

    # Additional environment from config
    env.update(config['env'])
    os.environ.update(env)

    os_env = {}

    ###
    # Databases
    ###
    if 'postgresql' in config['modules']:
        start_postgresql()
        os_env['POSTGRESQL_DB'] = 'pype_webapp'
        os_env['POSTGRESQL_USER'] = 'pype_webapp'
        os_env['POSTGRESQL_PASS'] = 'pype_webapp'
    if 'redis' in config['modules']:
        start_redis()
    if 'persistent_dir' in config['modules']:
        # TODO: Create a persistent directory and pass it as environment variable
        pass

    os.environ.update(os_env)

    ###
    # Virtualenv
    ###
    if os.path.exists('requirements.txt.lock'):
        requirements_file = 'requirements.txt.lock'
    elif os.path.exists('requirements.txt'):
        requirements_file = 'requirements.txt'
    elif os.path.exists('setup.py'):
        requirements_file = 'setup.py'
    else:
        requirements_file = None

    if requirements_file is not None:
        # Found requirements.txt -> Setting up a virtualenv and install requirements
        pyenv_path = '.pyenv'
        wheels_dir = 'py_wheels'

        # Configure pypi mirror
        #setup_pypi_mirror()

        # Create and configure the virtualenv
        if config['python_version'] == 'python3':
            setup_venv_py3(pyenv_path)
        else:
            setup_venv(pyenv_path)
        os.environ['PATH'] = os.path.join(pyenv_path, 'bin') + os.pathsep + os.environ['PATH']
        upgrade_pip()

        # Populate it
        if requirements_file == 'setup.py':
            _pip_exec(['install', '-q', './'])
            _pip_exec(['install', '-q', 'wheel'])
        else:
            build_wheel_cache(wheels_dir, ['-r', requirements_file])

        # Create requirements.txt.lock if it doesn't already exist
        if requirements_file == 'requirements.txt':
            # Write requirements.txt.lock
            frozen_reqs = freeze_requirements()
            with open('requirements.txt.lock', 'w') as fh:
                fh.write(frozen_reqs)

    ###
    # Npm
    ###
    if os.path.exists('package.json'):
        # Run npm install
        _exec([
            '/usr/bin/env', 'npm', 'install', '--loglevel=warn', '--no-progress'
        ])

    ###
    # Django
    ###
    if os.path.exists('manage.py'):
        # Assuming a django project -> create directories and build assets
        os_env['DJANGO_MODE'] = 'Jenkins'
        main_module = _extract_django_module_from_manage_py()
        if main_module is None:
            raise RuntimeError('Could not parse manage.py. Unable to guess the main application module name')
        os_env['DJANGO_SETTINGS_MODULE'] = main_module + '.settings'
        os.environ.update(os_env)

        _create_dir('logs')
        _create_dir('media')
        _exec([
            '/usr/bin/env', 'python', 'manage.py', 'collectstatic', '--noinput'
        ])
        _exec([
            '/usr/bin/env', 'python', 'manage.py', 'assets', 'build'
        ])

    ###
    # Bower
    ###
    if os.path.exists('bower.json'):
        # Install bower_components?
        pass

    create_build_info(version=args.version)

    ###
    # Webpack
    ###
    if os.path.exists('webpack.prod.js'):
        _exec([
            './node_modules/webpack/bin/webpack.js',
            '--config',
            'webpack.prod.js'
        ])
    elif os.path.exists('webpack.config.js'):
        _exec([
            './node_modules/webpack/bin/webpack.js'
        ])

    ###
    # Tests
    ###
    if os.path.exists('karma.conf.js'):
        # Run javascript tests
        #
        # xvfb-run -s "-screen 0 1280x720x16" ./node_modules/karma/bin/karma start
        # => Let the user figure out the command? Maho does the xvfb-run, and the user supplies the command?
        pass

    if os.path.exists('pytest.ini'):
        pass

    for test_command in config['test_commands']:
        _exec([
            'xvfb-run',
            '-s',
            '-screen 0 1280x720x16',
            '-a',
            #'-e',
            #'/dev/stdout'
        ] + shlex.split(test_command))

    ###
    # Python packages
    ###
    if os.path.exists('setup.py'):
        _exec([
            '/usr/bin/env',
            'python',
            'setup.py',
            'register',
            '-r',
            'devpi_luna'
        ])

        _exec([
            '/usr/bin/env',
            'python',
            'setup.py',
            'sdist',
            '--formats=gztar,zip',
            'bdist_wheel',
            'upload',
            '-r',
            'devpi_luna'
        ])

    ###
    # Generate archive
    ###
    exclude_paths = [
        'logs',
        'media',
        '.git',
        #'node_modules',
        #'bower_components',
        '.pyenv',
    ]
    output_name = config['project']
    _gen_archive(output_name, exclude_paths, version=args.version)


###
# The deploy command
###
nginx_template_text = """
worker_processes 1;

error_log   {{ root_dir }}/nginx.error.log warn;
pid         {{ root_dir }}/nginx.pid;

daemon off;

events {
    worker_connections  1024;
}

http {
    include /etc/nginx/mime.types;
    default_type    application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$scheme $host $server_port $request_time $status '
                      '$body_bytes_sent "$http_referer" '
                      '"$http_user_agent"';


    access_log  {{ root_dir }}/nginx.access.log  main;

    sendfile        on;

    keepalive_timeout 65;

    client_body_temp_path {{ root_dir }}/tmp/nginx_client_temp;
    proxy_temp_path {{ root_dir }}/tmp/nginx_proxy_temp;
    fastcgi_temp_path {{ root_dir }}/tmp/nginx_fastcgi_temp;
    uwsgi_temp_path {{ root_dir }}/tmp/nginx_uwsgi_temp;
    scgi_temp_path {{ root_dir }}/tmp/nginx_scgi_temp;

    {{ nginx_server_block }}

}
"""

uwsgi_template_text = """
[uwsgi]
plugins-dir=/usr/local/lib/uwsgi
plugin={{ python_plugin_version }}
chdir={{ deploy_dir }}
virtualenv={{ deploy_dir }}/venv
module={{ uwsgi_callable }}
master=True
pidfile={{ root_dir }}/uwsgi.{{ uwsgi_appname }}.pid
socket={{ root_dir }}/uwsgi.{{ uwsgi_appname }}.sock
{% for key, value in uwsgi_env.items() %}
env={{ key }}={{ value }}
{% endfor %}
processes=10
vacuum=True
max-requests=5000
stats={{ root_dir }}/uwsgi.{{ uwsgi_appname }}.stats.sock
logger=syslog:uwsgi.{{ deployment_name }}.{{ uwsgi_appname }}
"""

supervisor_template_text = """
[unix_http_server]
file={{ root_dir }}/supervisor.sock                       ; path to your socket file

[supervisord]
logfile={{ root_dir }}/supervisord.log    ; supervisord log file
logfile_maxbytes=50MB                           ; maximum size of logfile before rotation
logfile_backups=10                              ; number of backed up logfiles
loglevel=error                                  ; info, debug, warn, trace
pidfile={{ root_dir }}/supervisord.pid                ; pidfile location
nodaemon=false                                  ; run supervisord as a daemon
minfds=1024                                     ; number of startup file descriptors
minprocs=200                                    ; number of process descriptors
user=root                                       ; default user
childlogdir={{ root_dir }}/               ; where child log files will live

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://{{ root_dir }}/supervisor.sock         ; use a unix:// URL  for a unix socket

{% for command in supervisor_commands %}
[program:{{ command.name }}]
command={{ command.command_line }}
directory={{ deploy_dir }}
environment={{ command.environment_string }}
stdout_logfile = syslog
autorestart = true
redirect_stderr = true
stopasgroup = true
killasgroup = true
{% for config_line in command.config %}{{ config_line }}
{% endfor %}
{% endfor %}
"""


def gen_deployment_id():
    date = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    return date


def deploy(args):
    from jinja2 import Template
    # Extract archive
    archive_path = args.source_archive

    root_dir = os.getcwd()
    deployment_id = gen_deployment_id()
    deploy_dir = os.path.join(root_dir, 'deployment-%s' % deployment_id)

    try:
        shutil.rmtree(deploy_dir)
    except:
        pass

    _create_dir(deploy_dir)

    _exec([
        '/usr/bin/env',
        'tar',
        '-C',
        deploy_dir,
        '-xf',
        archive_path
    ])

    # Load config data
    user = pwd.getpwuid(os.getuid()).pw_name

    app_config = load_config(source_dir=deploy_dir)
    deployment_config = load_deployment_config()

    config_env = {
        'user': user,
        'root_dir': root_dir,
        'deploy_dir': deploy_dir,
        'listen_port': deployment_config['listen_port'],
        'deployment_name': deployment_config['deployment_name']
    }

    os_env = {}
    os_env.update(deployment_config['env'])

    supervisor_commands = app_config['daemon_commands']
    uwsgi_apps = app_config['uwsgi_apps']

    new_files = []

    _create_dir(os.path.join(root_dir, 'tmp'))

    if 'persistent_dir' in app_config['modules']:
        persistent_dir = os.path.join(root_dir, 'application_data')
        _create_dir(persistent_dir)
        os_env['PERSISTENT_DIR'] = persistent_dir

    if 'postgresql' in app_config['modules']:
        os_env['POSTGRESQL_DB'] = deployment_config['POSTGRESQL_DB']
        os_env['POSTGRESQL_USER'] = deployment_config['POSTGRESQL_USER']
        os_env['POSTGRESQL_PASS'] = deployment_config['POSTGRESQL_PASS']
        os.environ.update(os_env)

    # Create virtualenv
    if os.path.exists(os.path.join(deploy_dir, 'requirements.txt.lock')):
        requirements_file = os.path.join(deploy_dir, 'requirements.txt.lock')
    else:
        requirements_file = None

    if requirements_file is not None:
        virtualenv_dir = os.path.join(deploy_dir, 'venv')
        wheels_dir = os.path.join(deploy_dir, 'py_wheels')
        if app_config['python_version'] == 'python3':
            setup_venv_py3(virtualenv_dir)
        else:
            setup_venv(virtualenv_dir)
        os.environ['PATH'] = os.path.join(virtualenv_dir, 'bin') + os.pathsep + os.environ['PATH']
        os_env['PATH'] = os.environ['PATH']
        upgrade_pip()
        install_from_wheel_cache(wheels_dir, ['-r', requirements_file])

    # Install additional files
    if 'additional_files' in deployment_config:
        oldpwd = os.getcwd()
        os.chdir(deploy_dir)
        for target_path in deployment_config['additional_files'].keys():
            shutil.copy(
                deployment_config['additional_files'][target_path],
                target_path
            )

        os.chdir(oldpwd)

    ###
    # Django
    ###
    if os.path.exists(os.path.join(deploy_dir, 'manage.py')):
        oldpwd = os.getcwd()
        os.chdir(deploy_dir)
        # Assuming a django project -> create directories and build assets
        main_module = _extract_django_module_from_manage_py()
        if main_module is None:
            raise RuntimeError('Could not parse manage.py. Unable to guess the main application module name')

        _create_dir('logs')
        _create_dir('tmp')

        shutil.copy(deployment_config['secrets_path'], os.path.join(main_module, 'settings', 'secrets.json'))

        # Migrate
        _exec([
            '/usr/bin/env',
            'python',
            'manage.py',
            'migrate',
            '--noinput'
        ])

        uwsgi_apps.append({
            'name': 'django',
            'callable': main_module + '.wsgi:application',
            'env': {
                'DJANGO_SETTING_MODULE': main_module + '.settings'
            }
        })

        os.chdir(oldpwd)

    # Generate nginx config
    nginx_app_template_path = os.path.join(deploy_dir, 'deploy/nginx.conf')
    if os.path.exists(nginx_app_template_path):
        with open(nginx_app_template_path, 'r') as fh:
            nginx_app_template_text = fh.read()

        nginx_app_template = Template(nginx_app_template_text)
        nginx_app_template_rendered = nginx_app_template.render(config_env)

        nginx_env = deepcopy(config_env)
        nginx_env['nginx_server_block'] = nginx_app_template_rendered
        nginx_template = Template(nginx_template_text)
        nginx_template_rendered = nginx_template.render(nginx_env)

        nginx_rendered_path = os.path.join(root_dir, 'nginx.conf')
        new_files.append({
            'path': nginx_rendered_path,
            'content': nginx_template_rendered
        })

        supervisor_commands.append({
            'name': 'nginx',
            'command_line': '/usr/sbin/nginx -c "%s"' % nginx_rendered_path
        })

    # Generate uwsgi configs
    if len(uwsgi_apps) > 0:
        for uwsgi_app in uwsgi_apps:
            uwsgi_env = deepcopy(config_env)
            if app_config['python_version'] == 'python2':
                uwsgi_env['python_plugin_version'] = 'python27'
            else:
                uwsgi_env['python_plugin_version'] = 'python34'
            uwsgi_env['uwsgi_callable'] = uwsgi_app['callable']
            uwsgi_env['uwsgi_appname'] = uwsgi_app['name']
            uwsgi_env['uwsgi_env'] = uwsgi_app.get('env', {})
            uwsgi_template = Template(uwsgi_template_text)
            uwsgi_template_rendered = uwsgi_template.render(uwsgi_env)

            uwsgi_rendered_path = os.path.join(root_dir, 'uwsgi.%s.conf' % uwsgi_app['name'])
            new_files.append({
                'path': uwsgi_rendered_path,
                'content': uwsgi_template_rendered
            })

            supervisor_commands.append({
                'name': 'uwsgi.%s' % uwsgi_app['name'],
                'command_line': 'uwsgi --ini "%s"' % uwsgi_rendered_path
            })

    # Build the supervisor config file
    if len(supervisor_commands) == 0:
        # Nothing to run. This is weird
        raise RuntimeError('No supervisor commands defined to be ran.')

    supervisor_env = deepcopy(config_env)
    supervisor_env['supervisor_commands'] = supervisor_commands
    for cmd in supervisor_env['supervisor_commands']:
        e = os_env.copy()
        e.update(cmd.get('env', {}))
        cmd['environment_string'] = _make_supervisor_environment_string(e)
        cmd['config'] = cmd.get('config', [])
    supervisor_template = Template(supervisor_template_text)
    supervisor_template_rendered = supervisor_template.render(supervisor_env)

    supervisor_rendered_path = os.path.join(root_dir, 'supervisord.conf')
    new_files.append({
        'path': supervisor_rendered_path,
        'content': supervisor_template_rendered
    })

    # Write the new files
    for new_file in new_files:
        with open(new_file['path'], 'w') as fh:
            fh.write(new_file['content'])

    # Restart supervisor
    if os.path.exists(os.path.join(root_dir, 'supervisor.sock')):
        _exec(['/usr/bin/env', 'supervisorctl', '-c', supervisor_rendered_path, 'reread'])
        _exec(['/usr/bin/env', 'supervisorctl', '-c', supervisor_rendered_path, 'update'])
        _exec(['/usr/bin/env', 'supervisorctl', '-c', supervisor_rendered_path, 'restart', 'all'])
    else:
        _exec(['/usr/bin/env', 'supervisord', '-c', supervisor_rendered_path])


###
# Arguments parser
###
def main(args=None):
    parser = argparse.ArgumentParser('Maho')
    subparsers = parser.add_subparsers(metavar='command')


    f_parser = _argparse_function(
        subparsers,
        build,
        'build',
        'Builds the project in the current directory',
    )
    f_parser.add_argument('-v', '--build-version', dest='version', metavar='version')

    _argparse_function(
        subparsers,
        cache_dependencies,
        'cache-dependencies',
        'Fetches all dependencies of the project'
    )

    f_parser = _argparse_function(
        subparsers,
        deploy,
        'deploy',
        'Deploys a project from an archive',
    )
    f_parser.add_argument(dest='source_archive', metavar='source-archive')

    #
    # Main dispatch function
    #
    parsed_args = parser.parse_args(args=args)
    parsed_args.func(parsed_args)


if __name__ == '__main__':
    main()
