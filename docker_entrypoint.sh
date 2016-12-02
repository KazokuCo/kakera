#!/bin/bash

exec /usr/local/bin/gunicorn -b 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS} \
    --threads ${GUNICORN_THREADS} \
    --preload \
    kakera.wsgi
