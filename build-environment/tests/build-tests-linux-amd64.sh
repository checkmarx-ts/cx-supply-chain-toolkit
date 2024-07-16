#! /bin/bash

. ./common


tearDown()
{
    $DOCKER_RUN_PREFIX --entrypoint test -t test:tag -f /sandbox/resolver/ScaResolver 
    assertEquals 0 $?

    $DOCKER_RUN_PREFIX --entrypoint test -t test:tag -f /sandbox/cxonecli/cx 
    assertEquals 0 $?
}

GRADLE_ALPINE_BUILD_PARAMS="-t test:tag --build-arg BASE=gradle:8-jdk11-alpine"

testBuildGradleAlpineSuccess()
{
    $DOCKER_BUILD_PREFIX $GRADLE_ALPINE_BUILD_PARAMS --target=resolver-alpine ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildGradleAlpineBuildCustomUIDGIDSuccess()
{
    $DOCKER_BUILD_PREFIX --build-arg USER_ID=2048 --build-arg GROUP_ID=2048 $GRADLE_ALPINE_BUILD_PARAMS  --target=resolver-alpine ..

    $DOCKER_RUN_PREFIX --entrypoint getent -t test:tag passwd 2048 
    assertEquals 0 $?

    $DOCKER_RUN_PREFIX --entrypoint getent -t test:tag passwd resolver
    assertEquals 0 $?

    $DOCKER_RUN_PREFIX --entrypoint getent -t test:tag group 2048 
    assertEquals 0 $?

    $DOCKER_RUN_PREFIX --entrypoint getent -t test:tag group sca
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildNoBaseTargetsAlpineSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --target=resolver-alpine ..
    assertEquals 0 $?
    
    $DOCKER_DELETE

}

testBuildGradleAlpineBareSuccess()
{
    $DOCKER_BUILD_PREFIX $GRADLE_ALPINE_BUILD_PARAMS --target=resolver-alpine-bare ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}


testBuildGradleDebianUbuntuFocalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-focal --target=resolver-debian ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildGradleDebianUbuntuJammySuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-jammy --target=resolver-debian ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}


testBuildAmazonSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazonlinux:latest --target=resolver-amazon ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildRedhatUbi9Success()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi9:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildRedhatUbi9MinimalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi9-minimal:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildRedhatUbi8Success()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildRedhatUbi8MinimalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8-minimal:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildBuildpackDepsLatestSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=buildpack-deps:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildBuildpackDepsSidSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=buildpack-deps:sid --target=resolver-debian ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildEclipseTemurinSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=eclipse-temurin:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildAmazonCorretto8AmazonLinuxSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:8 --target=resolver-amazon ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildAmazonCorretto11AmazonLinuxSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:11 --target=resolver-amazon ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildAmazonCorretto8AlpineSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:8-alpine3.14 --target=resolver-alpine ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testBuildAmazonCorretto11AlpineSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:11-alpine3.14 --target=resolver-alpine ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testPureDebianSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=debian:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}

testUbuntuSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=ubuntu:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    $DOCKER_DELETE
}


testNoCreatingDirRedhat1()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8:latest --target=resolver-redhat ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    $DOCKER_DELETE
}

testNoCreatingDirRedhat2()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8-minimal:latest --target=resolver-redhat ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    $DOCKER_DELETE
}

testNoCreatingDirDebian()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=ubuntu:latest --target=resolver-debian ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    $DOCKER_DELETE
}

testNoCreatingDirAlpine()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:11-alpine3.14 --target=resolver-alpine ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    $DOCKER_DELETE
}

testNoCreatingDirAmazon()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:8 --target=resolver-amazon ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    $DOCKER_DELETE
}


. ./shunit2-2.1.8/shunit2

