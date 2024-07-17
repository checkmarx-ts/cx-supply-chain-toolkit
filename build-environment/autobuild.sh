#!/bin/bash
set -e

## A script to automatically build
## Options
## -t : tag of container to extend
## -d : Toolkit build-environment path
## -b : create a bare container
## -u : use current user's UID for the resolver user in the container
## -g : use the current user's GID for the resolver user in the container
## -v : verbose output
## -a : additional arguments to apply to "docker build"

## Outputs the tag of the built container on stdout

TOOLKIT_PATH=$(dirname ${BASH_SOURCE[0]})
VERBOSITY_ARG="-q"

while getopts "t:d:a:bugpv" opt; do

  case ${opt} in

    t)
        SRC_TAG=${OPTARG}
        [[ "$SRC_TAG" =~ ":" ]] && TAG_VERSION=$(echo $SRC_TAG | cut -d : -f 2) || TAG_VERSION="latest"
        [ "$TAG_VERSION" == "" ] && TAG_VERSION="latest"
        DEST_TAG=$(echo $SRC_TAG | cut -d : -f 1)-resolver:$TAG_VERSION
        BASE_ARG="--build-arg BASE=$SRC_TAG"
    ;;

    b)
        TARGET_SUFFIX="-bare"
    ;;

    a)
        BUILD_ARGS=$(echo ${OPTARG} | tr -d '"')
    ;;

    u)
        UID_ARG="--build-arg USER_ID=$(id -u)"
    ;;

    g)
        GID_ARG="--build-arg GROUP_ID=$(id -g)"
    ;;

    d)
        TOOLKIT_PATH=$(realpath ${OPTARG})
    ;;

    v)
        VERBOSITY_ARG="--progress plain"
    ;;

  esac

done

[ "$DEST_TAG" == "" ] && echo "ERROR: tag of container to extend is required" && exit 1 >&2 || :
_=$(docker pull "$SRC_TAG")

set +e

IDENTIFIER=$(docker run --rm --entrypoint cat $SRC_TAG /etc/os-release | grep -E "ID|ID_LIKE")

[ -z $TARGET ] && echo $IDENTIFIER | grep -q -E "(ID|ID_LIKE)=.?amzn.?"
[ "$?" -eq "0" ] && TARGET=resolver-amazon$TARGET_SUFFIX

[ -z $TARGET ] && echo $IDENTIFIER | grep -q -E "(ID|ID_LIKE)=.?alpine.?"
[ "$?" -eq "0" ] && TARGET=resolver-alpine$TARGET_SUFFIX

[ -z $TARGET ] && echo $IDENTIFIER | grep -q -E "(ID|ID_LIKE)=.?debian.?"
[ "$?" -eq "0" ] && TARGET=resolver-debian$TARGET_SUFFIX

[ -z $TARGET ] && echo $IDENTIFIER | grep -q -E "(ID|ID_LIKE)=.?(rhel|fedora).?"
[ "$?" -eq "0" ] && TARGET=resolver-redhat$TARGET_SUFFIX

[ -z $TARGET ] && TARGET=unknown

set -e

_=$(docker build --pull $VERBOSITY_ARG -t "$DEST_TAG" $BASE_ARG $GID_ARG $UID_ARG --target $TARGET $BUILD_ARGS "$TOOLKIT_PATH")

echo $DEST_TAG
