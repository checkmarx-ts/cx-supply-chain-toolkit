#!/bin/sh

set -eu

trap $(exit $?) > /dev/null 2>&1

umask 0057

/sandbox/resolver/ScaResolver -c /resolver/Configuration.yml --scan-path /code $([[ $# -eq 0 ]] && echo "-h" || :) $@
