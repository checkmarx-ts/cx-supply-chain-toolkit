#!/bin/sh

set -eu

trap $(exit $?) >> /dev/null 2>&1

umask 0047

EXTRA=$($(which bash) -c "[[ $# -eq 0 ]] && echo \"-h\" || :")

ScaResolver $@ -c /sandbox/resolver/Configuration.yml $EXTRA
