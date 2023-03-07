#! /bin/bash

. ./common

PROJECT_DEFAULT_NAME="sca-resolver-sandbox-automated-test"


setUp()
{
    [ ! -d $OUTPUT_DIR ] && mkdir -p $OUTPUT_DIR || :
    [ ! -d $INPUT_DIR ] && mkdir -p $INPUT_DIR || :

}

tearDown()
{
    rm -rf $OUTPUT_DIR
    rm -rf $INPUT_DIR
}

oneTimeSetUp() {
    git clone https://github.com/checkmarx-ltd/cx-flow.git $(pwd)/cxflow
    $DOCKER_BUILD_PREFIX $BUILD_COMPAT -t test --build-arg BASE=gradle:8-jdk11-alpine --target=resolver-alpine ..
}

oneTimeTearDown() {
    [ -d "cxflow" ] && rm -rf cxflow || :
}

testNoArgsShowsHelp() {
    $DOCKER_RUN_PREFIX test > output/out.txt
    EXEC_RESULT=$?
    assertTrue 0 "[ $EXEC_RESULT -eq 0 -a $(wc -l output/out.txt | cut -d ' ' -f1) -gt 1 ]"
}

testHelpSameAsNoArgs() {
    $DOCKER_RUN_PREFIX test > output/noargs_out.txt
    EXEC_RESULT_NOARGS=$?

    $DOCKER_RUN_PREFIX test help > output/args_out.txt
    EXEC_RESULT_ARGS=$?

    assertTrue 0 "[ $EXEC_RESULT_NOARGS -eq $EXEC_RESULT_ARGS -a $(wc -l output/noargs_out.txt | cut -d ' ' -f1) -eq $(wc -l output/args_out.txt | cut -d ' ' -f1) ]"
}

testOfflineScanOfCxFlow () {

    cp -r $(pwd)/cxflow/* $INPUT_DIR

    $DOCKER_RUN_PREFIX test \
        offline \
        -s /sandbox/input \
        -n $PROJECT_DEFAULT_NAME \
        -r /sandbox/output/results.json > /dev/null 2>&1

    assertTrue 0 "[ -e ${OUTPUT_DIR}/results.json ]"
}

reportMissingVars() {
    echo Skipping test $1 due to missing environment variables:
    [ -z "${TEST_TENANT}" ] && echo TEST_TENANT
    [ -z "${TEST_USER}" ] && echo TEST_USER
    [ -z "${TEST_PASSWORD}" ] && echo TEST_PASSWORD
}

isMissingVars() {
    [[ -z "${TEST_TENANT}" || -z "${TEST_USER}" || -z "${TEST_PASSWORD}" ]] && return 0 || return 1 
}

testTwoStageScan () {
    
    if isMissingVars
    then
        startSkipping
        reportMissingVars "${FUNCNAME[0]}"
    else
        cp -r $(pwd)/cxflow/* $INPUT_DIR

        $DOCKER_RUN_PREFIX test \
            offline \
            -s /sandbox/input \
            -n $PROJECT_DEFAULT_NAME \
            -r /sandbox/output/results.json > /dev/null 2>&1

        rm -rf $INPUT_DIR/*
        mv $OUTPUT_DIR/results.json $INPUT_DIR/results.json

        $DOCKER_RUN_PREFIX test \
            upload \
            --report-path=/sandbox/output \
            --report-type=Risk \
            -a "${TEST_TENANT}" \
            -u "${TEST_USER}" \
            -p "${TEST_PASSWORD}" \
            -n $PROJECT_DEFAULT_NAME \
            --bypass-exitcode=True \
            -r /sandbox/input/results.json  > /dev/null 2>&1

    fi

    assertTrue 0 $?
    
    [[ isSkipping -eq "${SHUNIT_TRUE}" ]] && endSkipping
}






. ./shunit2-2.1.8/shunit2
