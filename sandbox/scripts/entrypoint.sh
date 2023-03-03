#!/bin/sh

set -eu

trap $(exit $?) >> /dev/null 2>&1

umask 0047

ScaResolver $@ -c /sandbox/resolver/Configuration.yml --scan-path /sandbox/code $([[ $# -eq 0 ]] && echo "-h" || :)
