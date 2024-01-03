#!/bin/bsh

set -eu

trap $(exit $?) >> /dev/null 2>&1

umask 0047

# Move code to a place where it is read/write
cp -r /sandbox/input /sandbox/input_sandbox

SKIP_SCA=0

if [[ $# -ne 0 ]]; then

    case $1 in
        cxone)
            SKIP_SCA=1
            shift

            /sandbox/cxonecli/cx $@

        ;;

        sca)
            shift
        ;;

        *)
        ;;
    esac
fi


if [[ $SKIP_SCA -eq 0 ]]; then
    EXTRA=$($(which bash) -c "[[ $# -eq 0 ]] && echo \"-h\" || echo -c /sandbox/resolver/Configuration.yml")

    /sandbox/resolver/ScaResolver $@ $EXTRA
fi
