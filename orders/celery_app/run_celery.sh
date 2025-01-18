#!/usr/bin/env bash

mkdir -p /var/run/celery /var/log/celery
chown -R nobody:nogroup /var/run/celery /var/log/celery

exec celery --app=celery_app.celery_app worker \
            --loglevel=INFO \
            --logfile=/var/log/celery/celery_worker.log \
            --statedb=/var/run/celery/celery_worker@%h.state \
            --hostname=celery_app@%h \
            -O fair -c 1 \
            --uid=nobody --gid=nogroup
