#!/bin/bash

CXFLOW_JAR=/app/cx-flow.jar

set -e
umask 0047

. $(dirname $0)/funcs

[ "$1" = "_VERSIONONLY_" ] && { getCxFlowJarVersion $CXFLOW_JAR ; exit 0 ; }

cat banner.txt

bannerBegin "Default CxFlow Version Check (${CXFLOW_JAR})"
displayCxFlowVersionInfo $CXFLOW_JAR
bannerEnd "Default CxFlow Version Check (${CXFLOW_JAR})"


if [ ! -z "${CXFLOW_ALT_JAR_URL}" ]
then

    bannerBegin "Replacing CxFlow Jar"
    wget -nv -P /alt $CXFLOW_ALT_JAR_URL
    bannerEnd "Replacing CxFlow Jar"

    CXFLOW_JAR=$(ls /alt/*.jar)

    bannerBegin "CxFlow Replacement Version Check (${CXFLOW_JAR})"
    displayCxFlowVersionInfo $CXFLOW_JAR
    bannerEnd "CxFlow Replacement Version Check (${CXFLOW_JAR})"

fi

if [ ! -z "${CXFLOW_YAML_URL}" ]
then
    bannerBegin "Downloading Yaml Configuration"
    wget -nv -P /yaml $CXFLOW_YAML_URL
    CONFIG_YAML=$(ls /yaml)
    echo Using $CONFIG_YAML
    CONFIG_PARAM="--spring.config.location=/yaml/${CONFIG_YAML}"
    bannerEnd "Downloading Yaml Configuration"
fi



if [ ! -z "${SCA_PATH_TO_SCA_RESOLVER}" ]
then
    echo WARNING: You have define the path to SCAResolver as: $SCA_PATH_TO_SCA_RESOLVER
    echo WARNING: The SCA Resolver path is managed by this container and is not user configurable.
    unset SCA_PATH_TO_SCA_RESOLVER
fi


java $JAVA_OPTS $JAVA_PROPS $SPRING_PROPS -jar $CXFLOW_JAR $@ $CONFIG_PARAM --sca.path-to-sca-resolver=""

exit $?
