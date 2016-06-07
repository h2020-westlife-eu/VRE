server: python manage.py runserver 0.0.0.0:8000
celery_worker: C_FORCE_ROOT=1 celery -A pype worker -B -l info --concurrency 1
ws_server: python manage.py ws_server --listen_address 0.0.0.0
coverage_http_server: python -m SimpleHTTPServer 8069