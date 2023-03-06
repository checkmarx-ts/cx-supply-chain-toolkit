#! /bin/sh

. ./common


tearDown()
{
    [ $(docker image ls test:tag | wc -l) -gt 1 ] && docker image rm test:tag
    docker system prune -f
}

testBuildGradleAlpine()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-alpine --target=resolver-alpine ..
    assertEquals 0 $?
}

testBuildNoBaseTargetsAlpineSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --target=resolver-alpine ..
    assertEquals 0 $?
}

testBuildNoBaseTargetsNonAlpineFails()
{
    $DOCKER_BUILD_PREFIX -t test:tag --target=resolver-alpine --target=resolver-redhat ..
    assertNotEquals 0 $?
}

testBuildGradleDebianUbuntuFocalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-focal --target=resolver-debian ..
    assertEquals 0 $?
}

testBuildGradleDebianUbuntuJammySuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-jammy --target=resolver-debian ..
    assertEquals 0 $?
}

testBuildGradleWrongTypeFails()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-jammy --target=resolver-redhat ..
    assertNotEquals 0 $?
}

testBuildAmazonSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazonlinux:latest --target=resolver-amazon ..
    assertNotEquals 0 $?
}

testBuildRedhatUbi9Success()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi9:latest --target=resolver-redhat ..
    assertNotEquals 0 $?
}

testBuildRedhatUbi9MinimalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi9-minimal:latest --target=resolver-redhat ..
    assertNotEquals 0 $?
}

testBuildRedhatUbi8Success()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8:latest --target=resolver-redhat ..
    assertNotEquals 0 $?
}

testBuildRedhatUbi8MinimalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8-minimal:latest --target=resolver-redhat ..
    assertNotEquals 0 $?
}

. shunit2-2.1.8/shunit2
