#!/bin/sh

set -eu

trap $(exit $?) >> /dev/null 2>&1

umask 0047

cp -r /sandbox/input /sandbox/input_sandbox

EXTRA=$($(which bash) -c "[[ $# -eq 0 ]] && echo \"-h\" || echo -c /sandbox/resolver/Configuration.yml")

/sandbox/resolver/ScaResolver $@ $EXTRA
