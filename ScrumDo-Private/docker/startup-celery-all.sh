#!/bin/bash
cd /srv/scrumdo/scrumdo_web
export C_FORCE_ROOT='true'
exec celery worker -l info -A celeryconfig 
