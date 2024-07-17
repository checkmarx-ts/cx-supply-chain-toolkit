#! /bin/bash

. ./common

if [ ! -z "$BUILD_COMPAT" ]; then
    AUTOBUILDER="../autobuild.sh -a \"$BUILD_COMPAT\""
else
    AUTOBUILDER="../autobuild.sh"
fi

echo AUTOBUILDER: $AUTOBUILDER

tearDown()
{
    docker image inspect $TEST_TAG > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        $DOCKER_RUN_PREFIX --entrypoint test -t $TEST_TAG -f /sandbox/resolver/ScaResolver 
        assertEquals 0 $?

        $DOCKER_RUN_PREFIX --entrypoint test -t $TEST_TAG -f /sandbox/cxonecli/cx 
        assertEquals 0 $?

        echo Removing image $TEST_TAG
        docker image rm -f $TEST_TAG > /dev/null
        docker system prune -f > /dev/null
    fi
}

testFailOnBadTag()
{
    TEST_TAG=$($AUTOBUILDER -t foo)
    assertNotEquals 0 $?
}

testFailOnNoTag()
{
    TEST_TAG=$($AUTOBUILDER)
    assertNotEquals 0 $?
}

testFailOnBadToolkitDir()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -d /)
    assertNotEquals 0 $?
}

testBuildRegular()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG)
    assertEquals 0 $?
}

testBuildRegularExplicitToolkitDir()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -d ..)
    assertEquals 0 $?
}


testBuildBare()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -b)
    assertEquals 0 $?
}

testBuildBareExplicitToolkitDir()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -b -d ..)
    assertEquals 0 $?
}

testBuildBareNoInheritGID()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -b -g)
    assertEquals "Build step failure" 0 $?

    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -g | tr -d '\r\n') 0
}

testBuildRegularInheritGID()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -g)
    assertEquals "Build step failure" 0 $?

    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -g | tr -d '\r\n') $(id -g)
}

testBuildBareNoInheritUID()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -b -u)
    assertEquals "Build step failure" 0 $?

    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -u | tr -d '\r\n') 0
}

testBuildRegularInheritUID()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -u)
    assertEquals "Build step failure" 0 $?

    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -u | tr -d '\r\n') $(id -u)
}

testBuildBareNoInheritUIDOrGID()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -b -u -g)
    assertEquals "Build step failure" 0 $?

    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -u | tr -d '\r\n') 0
    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -g | tr -d '\r\n') 0
}

testBuildRegularInheritUIDAndGID()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -u -g)
    assertEquals "Build step failure" 0 $?

    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -u | tr -d '\r\n') $(id -u)
    assertEquals $($DOCKER_RUN_PREFIX --entrypoint id -t $TEST_TAG -g | tr -d '\r\n') $(id -g)
}

[ -z $BASE_IMG ] && echo Define BASE_IMG to run the tests && exit 1


. ./shunit2-2.1.8/shunit2
