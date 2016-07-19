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



### Extending the code

##### Adding static pages

A common task is to add static content pages to the site. The process to do this is the following:

* Clone this repository and follow the instructions to get a development application running
* Make a copy *ui/templates/static_pages/westlife/example.html* in the same directory, naming it however you want. Let's say *mycontent.html*
* Edit this file to add your content inside the "static_content" block. Note that you do _not_ have to write the entire page structure (<html>, <head>, header menu, etc). Only your content. Django will fill in the rest using standardized templates.
* Edit *ui/urls.py*. Here, we decide at what url your static page will be available. Add a line to the westlife_pages array, following the same structure as the "example" line. The example line says that /pages/example/ will point to *ui/templates/static_pages/westlife/example.html*. Replacing both 'example' should be all you have to do.
* If all went well, your static page should be available in your development environment.
* Commit everything and make a pull request

TODO:
* Update the menus so the pages can be found.