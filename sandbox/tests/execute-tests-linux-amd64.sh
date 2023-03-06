#! /bin/bash

. ./common

setUp()
{
    [ -d $OUTPUT_DIR ] && { rm -rf $OUTPUT_DIR ; mkdir -p $OUTPUT_DIR ; } || mkdir -p $OUTPUT_DIR
    [ -d $INPUT_DIR ] && { rm -rf $INPUT_DIR ; mkdir -p $INPUT_DIR ; } || mkdir -p $INPUT_DIR

}

tearDown()
{
    rm -rf $OUTPUT_DIR
    rm -rf $INPUT_DIR
}

oneTimeSetUp() {
    git clone https://github.com/checkmarx-ltd/cx-flow.git cxflow


echo ----------------------------------
echo $DOCKER_RUN_PREFIX
[[ -z "${BUILD_COMPAT}" ]] && echo NOT DEFINED || echo IT IS DEFINED
echo ----------------------------------


    $DOCKER_BUILD_PREFIX $BUILD_COMPAT -t test --build-arg BASE=gradle:8-jdk11-alpine --target=resolver-alpine ..

docker image ls

   
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

. ./shunit2-2.1.8/shunit2
