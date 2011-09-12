#!/usr/bin/env python

import logging
import os
import sys

log = logging.getLogger(__name__)


def post_activate(args):
    pass


def post_activate_source(args):

    # Import the settings needed for Django-environment
    VIRTUAL_ENV = os.getenv('VIRTUAL_ENV')
    VIRTUAL_ENV_BIN = os.path.join(VIRTUAL_ENV, 'bin')
    DJANGO_ENV_SETTINGS_FILE = os.path.join(VIRTUAL_ENV_BIN, 'django_env_settings.py')
    sys.path.append(VIRTUAL_ENV_BIN)
    try:
        import django_env_settings
    except ImportError:
        print "ERROR: Your Django-environment settings file was missing (%s)." % DJANGO_ENV_SETTINGS_FILE
        return

    # Get Django-environment settings to add to shell environment variables
    DJANGO_ENV_PROJECT_DIR = getattr(django_env_settings, 'DJANGO_ENV_PROJECT_DIR', False)
    DJANGO_SETTINGS_MODULE = getattr(django_env_settings, 'DJANGO_ENV_SETTINGS_MODULE', False)
    DJANGO_ENV_SERVER_ADDR = getattr(django_env_settings, 'DJANGO_ENV_SERVER_ADDR', '127.0.0.1')
    DJANGO_ENV_SERVER_PORT = getattr(django_env_settings, 'DJANGO_ENV_SERVER_PORT', '8000')
    DJANGO_ENV_FABFILE = getattr(django_env_settings, 'DJANGO_ENV_FABFILE', False)

    # Error messages
    MISSING_SETTINGS_ERROR = 'ERROR: The setting "%s" was missing from your Django-environment settings file (%s)'
    DJANGO_ENV_ACTIVATED_MSG = """Your Django-environment "%s" has been activated.

Django-environment Commands:
runserver      Starts the Django development server
deactivate     Deactivates the current Django-environment
workon <name>  Work on a different Django-environment""" % os.path.basename(VIRTUAL_ENV)

    # Check for required settings
    if not DJANGO_ENV_PROJECT_DIR:
        print MISSING_SETTINGS_ERROR % ('DJANGO_ENV_PROJECT_DIR', DJANGO_ENV_SETTINGS_FILE)
    if not DJANGO_SETTINGS_MODULE:
        print MISSING_SETTINGS_ERROR % ('DJANGO_SETTINGS_MODULE', DJANGO_ENV_SETTINGS_FILE)

    SHELL_SOURCE_RETURN = """

alias cddjango_project="cd %s"
export DJANGO_ENV_PROJECT_DIR=%s
export DJANGO_SETTINGS_MODULE=%s
export DJANGO_ENV_SERVER_ADDR=%s
export DJANGO_ENV_SERVER_PORT=%s

function runserver {
    if [ -n "$DJANGO_ENV_SERVER_ADDR" -a -n "$DJANGO_ENV_SERVER_PORT" ]; then
        django-admin.py runserver $DJANGO_ENV_SERVER_ADDR:$DJANGO_ENV_SERVER_PORT
    elif [ -n "$DJANGO_SERVER_PORT" ]; then
        django-admin.py runserver $DJANGO_ENV_SERVER_PORT
    else
        django-admin.py runserver
    fi
}

cddjango_project
""" % (DJANGO_ENV_PROJECT_DIR, DJANGO_ENV_PROJECT_DIR, DJANGO_SETTINGS_MODULE, DJANGO_ENV_SERVER_ADDR, DJANGO_ENV_SERVER_PORT)

    if DJANGO_ENV_FABFILE:
        SHELL_SOURCE_RETURN += 'alias fab="fab -f %s"' % DJANGO_ENV_FABFILE
        DJANGO_ENV_ACTIVATED_MSG += "\nfab <command>  Run fabric commands in your fabfile.py for this Django project."

    SHELL_SOURCE_RETURN += "\necho '\n%s\n'" % DJANGO_ENV_ACTIVATED_MSG
    return SHELL_SOURCE_RETURN


def post_deactivate(args):
    pass


def post_deactivate_source(args):
    return """
# remove all enviroment variables prefixed with DJANGO
if [ -n "$(env | grep DJANGO_ENV)" ]; then
    for i in $(env | grep DJANGO_ENV | perl -lne "s/(django_env[_a-z]+)=.+/\\1/ig; print;"); do unset $i; done
fi

# remove the alias to the fabfile.py for this project
if [ -n "$(alias | grep 'alias fab')" ]; then
    unalias fab
fi"""



def post_mkvirtualenv(args):
    log.info('post_mkvirtualenv ran %s' % args)
