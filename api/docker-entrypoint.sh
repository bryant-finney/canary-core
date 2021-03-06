#!/bin/sh
# shellcheck shell=sh
# -------------------------------------------------------------------------------------
# Summary: Peform standard initialization commands using the entrypoint script.
# Created: 2021-11-10 21:31:17
# Author:  Bryant Finney (https://bryant-finney.github.io/about)
# -------------------------------------------------------------------------------------

echo "running migrations"
django-admin migrate --no-input

echo "collecting static files"
django-admin collectstatic --no-input

# shellcheck disable=SC2068
$@
