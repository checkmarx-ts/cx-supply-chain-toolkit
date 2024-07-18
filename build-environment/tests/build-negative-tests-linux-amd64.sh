#! /bin/bash

. ./common


testBuildNoBaseTargetsNonAlpineFails()
{
    $DOCKER_BUILD_PREFIX -t test:tag --target=resolver-redhat ..
    assertNotEquals 0 $?
}


testBuildGradleWrongTypeFails()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-jammy --target=resolver-redhat ..
    assertNotEquals 0 $?
}

. ./shunit2-2.1.8/shunit2
