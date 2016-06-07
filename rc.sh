#!/usr/bin/env bash

VENV_DIR=".pyvenv"
APP_NAME="pype"

export DJANGO_MODE=Dev
export DJANGO_SETTINGS_MODULE=${APP_NAME}.settings
source "${VENV_DIR}/bin/activate"

alias run="python manage.py runserver 0.0.0.0:8000"
alias test="py.test --cov-report term --cov-report html"
alias test_noreuse="test --create-db"
alias celery_worker="C_FORCE_ROOT=1 celery -A ${APP_NAME} worker -B -l info"