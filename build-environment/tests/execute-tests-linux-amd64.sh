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
    git clone --depth=1 https://github.com/WebGoat/WebGoat.git $(pwd)/webgoat
    $DOCKER_BUILD_PREFIX -t test --build-arg BASE=cimg/openjdk:17.0 --target=resolver-debian ..
}

oneTimeTearDown() {
    [ -d "webgoat" ] && rm -rf webgoat || :
}

testNoArgsShowsHelp() {
    $DOCKER_RUN_PREFIX test > output/out.txt
    EXEC_RESULT=$?
    assertTrue 0 "[ $EXEC_RESULT -eq 0 -a $(wc -l output/out.txt | cut -d ' ' -f1) -gt 1 ]"
}

testNoArgsCxOneShowsHelp() {
    $DOCKER_RUN_PREFIX test cxone > output/out.txt
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

testHelpSameAsScaArgs() {
    $DOCKER_RUN_PREFIX test > output/noargs_out.txt
    EXEC_RESULT_NOARGS=$?

    $DOCKER_RUN_PREFIX test sca help > output/args_out.txt
    EXEC_RESULT_ARGS=$?

    assertTrue 0 "[ $EXEC_RESULT_NOARGS -eq $EXEC_RESULT_ARGS -a $(wc -l output/noargs_out.txt | cut -d ' ' -f1) -eq $(wc -l output/args_out.txt | cut -d ' ' -f1) ]"
}

testCxOneHelpSameAsNoArgs() {
    $DOCKER_RUN_PREFIX test cxone > output/noargs_out.txt
    EXEC_RESULT_NOARGS=$?

    $DOCKER_RUN_PREFIX test cxone help > output/args_out.txt
    EXEC_RESULT_ARGS=$?

    assertTrue 0 "[ $EXEC_RESULT_NOARGS -eq $EXEC_RESULT_ARGS -a $(wc -l output/noargs_out.txt | cut -d ' ' -f1) -eq $(wc -l output/args_out.txt | cut -d ' ' -f1) ]"
}

testOfflineResolverScanOfWebgoat () {

    cp -r $(pwd)/webgoat/* $INPUT_DIR

    $DOCKER_RUN_PREFIX test \
        offline \
        -s /sandbox/input \
        -n $PROJECT_DEFAULT_NAME \
        -r /sandbox/output/results.json > /dev/null 2>&1

    assertTrue 0 "[ -e ${OUTPUT_DIR}/results.json ]"
}

reportMissingScaVars() {
    echo Skipping test $1 due to missing SCA environment variables:
    [ -z "${TEST_TENANT}" ] && echo TEST_TENANT
    [ -z "${TEST_USER}" ] && echo TEST_USER
    [ -z "${TEST_PASSWORD}" ] && echo TEST_PASSWORD
}

isMissingScaVars() {
    [[ -z "${TEST_TENANT}" || -z "${TEST_USER}" || -z "${TEST_PASSWORD}" ]] && return 0 || return 1 
}

reportMissingCxOneVars() {
    echo Skipping test $1 due to missing CxOne environment variables:
    [ -z "${TEST_APIKEY}" ] && echo TEST_APIKEY
}

isMissingCxOneVars() {
    [[ -z "${TEST_APIKEY}" ]] && return 0 || return 1 
}

testTwoStageScanOfWebgoat () {
    
    if isMissingScaVars
    then
        startSkipping
        reportMissingScaVars "${FUNCNAME[0]}"
    else
        cp -r $(pwd)/webgoat/* $INPUT_DIR

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

testCxOneScan () {
    
    if isMissingCxOneVars
    then
        startSkipping
        reportMissingCxOneVars "${FUNCNAME[0]}"
    else
        cp -r $(pwd)/webgoat/* $INPUT_DIR

        $DOCKER_RUN_PREFIX test cxone \
            scan create \
            -s /sandbox/input \
            --project-name $PROJECT_DEFAULT_NAME \
            --output-path /sandbox/output \
            --sca-resolver /sandbox/resolver/ScaResolver \
            --scan-types sast,sca \
            --report-format json \
            --output-name .cxsca-results.json \
            --branch master \
            --apikey $TEST_APIKEY > /dev/null 2>&1

        rm -rf $INPUT_DIR/*
    fi

    assertTrue 0 $?
    
    [[ isSkipping -eq "${SHUNIT_TRUE}" ]] && endSkipping
}

testCxOneOfflineScaScan () {
    
    if isMissingCxOneVars
    then
        startSkipping
        reportMissingCxOneVars "${FUNCNAME[0]}"
    else
        cp -r $(pwd)/webgoat/* $INPUT_DIR

        $DOCKER_RUN_PREFIX test \
            offline \
            -s /sandbox/input \
            -n $PROJECT_DEFAULT_NAME \
            -r /sandbox/output/.cxsca-results.json > /dev/null 2>&1

        rm -rf $INPUT_DIR

        mv $OUTPUT_DIR $INPUT_DIR

        $DOCKER_RUN_PREFIX test cxone \
            scan create \
            -s /sandbox/input \
            --project-name $PROJECT_DEFAULT_NAME \
            --scan-types sca \
            --branch master \
            --apikey $TEST_APIKEY > /dev/null 2>&1

    fi

    assertTrue 0 $?
    
    [[ isSkipping -eq "${SHUNIT_TRUE}" ]] && endSkipping
}



. ./shunit2-2.1.8/shunit2
