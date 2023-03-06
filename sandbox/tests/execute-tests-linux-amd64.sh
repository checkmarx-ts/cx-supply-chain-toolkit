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
    git clone https://github.com/checkmarx-ltd/cx-flow.git cxflow
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

    ls -l

    echo ---------------------------
    $DOCKER_RUN_PREFIX --entrypoint="ls" test -l ..

    echo ---------------------------
    $DOCKER_RUN_PREFIX --entrypoint="whoami" test

    echo ---------------------------
    $DOCKER_RUN_PREFIX --entrypoint="groups" test

    echo ---------------------------
    $DOCKER_RUN_PREFIX --entrypoint="getent" test group gradle
    echo ---------------------------
    $DOCKER_RUN_PREFIX --entrypoint="getent" test passwd gradle


    $DOCKER_RUN_PREFIX test \
        offline \
        -s /sandbox/input \
        -n $PROJECT_DEFAULT_NAME \
        -r /sandbox/output/results.json

    assertTrue 0 "[ -e ${OUTPUT_DIR}/results.json ]"
}

. ./shunit2-2.1.8/shunit2
