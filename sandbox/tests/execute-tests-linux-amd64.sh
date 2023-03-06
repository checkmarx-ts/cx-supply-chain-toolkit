#! /bin/bash

. ./common

setUp()
{
    [ -d "output" ] && { rm -rf output ; mkdir output ; } || mkdir output
    [ -d "input" ] && { rm -rf input ; mkdir input ; } || mkdir input

}

tearDown()
{
    rm -rf output
    rm -rf input
}

oneTimeSetUp() {
    git clone https://github.com/checkmarx-ltd/cx-flow.git cxflow


echo ----- BEFORE BUILD
    docker image ls


    $DOCKER_BUILD_PREFIX --push -t test --build-arg BASE=gradle:8-jdk11-alpine --target=resolver-alpine ..

echo ----- AFTER BUILD
    docker image ls
   
}

oneTimeTearDown() {
    [ -d "cxflow" ] && rm -rf cxflow || :
}

testNoArgsShowsHelp() {
    echo -----------IN TEST----------
    docker image ls
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
