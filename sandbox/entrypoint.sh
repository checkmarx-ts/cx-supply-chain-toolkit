#!/bin/bash

set -eu

trap $(exit $?) >> /dev/null 2>&1

umask 0057

ScaResolver -c /resolver/Configuration.yml --scan-path /sandbox/code $([[ $# -eq 0 ]] && echo "-h" || :) $@
