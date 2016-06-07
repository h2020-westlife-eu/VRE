#!/bin/bash

source ./.pyvenv/bin/activate
export DJANGO_MODE=WestLifeProd
exec python manage.py "$@"
