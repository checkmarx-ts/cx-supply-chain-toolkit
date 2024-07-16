#! /bin/bash

. ./common


deleteImages()
{
    for img in $(docker image ls -a -q); do
        docker image rm -f $img
    done
    
    docker system prune -f
}


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
    
    deleteImages
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
    
    deleteImages
}

testBuildNoBaseTargetsAlpineSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --target=resolver-alpine ..
    assertEquals 0 $?
    
    deleteImages

}

testBuildGradleAlpineBareSuccess()
{
    $DOCKER_BUILD_PREFIX $GRADLE_ALPINE_BUILD_PARAMS --target=resolver-alpine-bare ..
    assertEquals 0 $?
    
    deleteImages
}


testBuildGradleDebianUbuntuFocalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-focal --target=resolver-debian ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildGradleDebianUbuntuJammySuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=gradle:8-jdk11-jammy --target=resolver-debian ..
    assertEquals 0 $?
    
    deleteImages
}


testBuildAmazonSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazonlinux:latest --target=resolver-amazon ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildRedhatUbi9Success()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi9:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildRedhatUbi9MinimalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi9-minimal:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildRedhatUbi8Success()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildRedhatUbi8MinimalSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8-minimal:latest --target=resolver-redhat ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildBuildpackDepsLatestSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=buildpack-deps:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildBuildpackDepsSidSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=buildpack-deps:sid --target=resolver-debian ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildEclipseTemurinSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=eclipse-temurin:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildAmazonCorretto8AmazonLinuxSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:8 --target=resolver-amazon ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildAmazonCorretto11AmazonLinuxSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:11 --target=resolver-amazon ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildAmazonCorretto8AlpineSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:8-alpine3.14 --target=resolver-alpine ..
    assertEquals 0 $?
    
    deleteImages
}

testBuildAmazonCorretto11AlpineSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:11-alpine3.14 --target=resolver-alpine ..
    assertEquals 0 $?
    
    deleteImages
}

testPureDebianSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=debian:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    deleteImages
}

testUbuntuSuccess()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=ubuntu:latest --target=resolver-debian ..
    assertEquals 0 $?
    
    deleteImages
}


testNoCreatingDirRedhat1()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8:latest --target=resolver-redhat ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    deleteImages
}

testNoCreatingDirRedhat2()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=redhat/ubi8-minimal:latest --target=resolver-redhat ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    deleteImages
}

testNoCreatingDirDebian()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=ubuntu:latest --target=resolver-debian ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    deleteImages
}

testNoCreatingDirAlpine()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:11-alpine3.14 --target=resolver-alpine ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    deleteImages
}

testNoCreatingDirAmazon()
{
    $DOCKER_BUILD_PREFIX -t test:tag --build-arg BASE=amazoncorretto:8 --target=resolver-amazon ..
    docker run --rm -it test:tag cxone | grep -i "creating directory"
    assertNotEquals 0 $?
    
    deleteImages
}


. ./shunit2-2.1.8/shunit2

