# West-Life VRE

### Installation


##### Required packages

* python 2.7
* redis-server
* postgresql
* NodeJS (See [https://nodejs.org/en/](https://nodejs.org/en/) for installation instructions)
* supervisor
* uwsgi
* postgresq-server-dev-all
* python-pip python-dev
* libffi-dev

##### Installation instructions

* Clone the repository
* bash make_venv.sh


##### Running in development mode

1. Create a postgresql database
2. Edit *pype/settings/dev.py* with the postgresql database name, user, password
2. From within the source directory, run:
````
$ source rc.sh
$ python manage.py migrate
$ honcho start
````


##### Running in production
The supported way to run the application is via uwsgi.

1. Create a postgresql database
2. Edit *pype/settings/prod.py* with your specific settings. The settings you are likely to need to change are:
  * *USE_SSL*
  * *DB_NAME*
  * *DB_USER*
  * *DB_PASS*
  * *ALLOWED_HOSTS*
  * *BASE_URL*
  * *MEDIA_ROOT*
3. Change the secret key in *pype/settings/secrets.json* to a long random string
4. Run
````
$ source rc.sh
$ export DJANGO_MODE=WestLifeProd
$ python manage.py migrate
$ python manage.py assets build
````
5. Edit *deploy/uwsgi.ini* and *deploy/pype.supervisord.conf* and adapt all paths.
6. Copy *pype.supervisord.conf* to */etc/supervisor/conf.d* and restart supervisor

The application should now be running on uwsgi://127.0.0.1:8101

You will need to configure your frontend web server to be able to access it. For apache, we recommend [mod_proxy_uwsgi](http://uwsgi-docs.readthedocs.io/en/latest/Apache.html#mod-proxy-uwsgi). For nginx, see [https://www.nginx.com/resources/admin-guide/gateway-uwsgi-django/](https://www.nginx.com/resources/admin-guide/gateway-uwsgi-django/)
