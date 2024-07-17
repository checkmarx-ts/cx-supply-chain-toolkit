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

        echo Removing images $TEST_TAG $BASE_IMG
        docker image rm -f $TEST_TAG $BASE_IMG
        docker system prune -f
    fi
}


testBuildRegularBuild()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG)
    assertEquals 0 $?
}

testBuildBareBuild()
{
    TEST_TAG=$($AUTOBUILDER -t $BASE_IMG -b)
    assertEquals 0 $?
}

[ -z $BASE_IMG ] && echo Define BASE_IMG to run the tests && exit 1


. ./shunit2-2.1.8/shunit2
