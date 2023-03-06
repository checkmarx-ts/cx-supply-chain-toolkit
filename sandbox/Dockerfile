ARG BASE=alpine:latest

##########################################################################
FROM ${BASE} AS base-config

ARG CONFIG_DIR=default-config
ARG GROUP_ID=1000
ARG USER_ID=1000

RUN mkdir -p /sandbox/scalogs && \
    chmod -R 730 /sandbox/scalogs && \
    mkdir -p /sandbox/input && \
    chmod -R 750 /sandbox/input && \
    mkdir -p /sandbox/output && \
    chmod -R 730 /sandbox/output && \
    mkdir -p /sandbox/resolver/cache && \
    chmod -R 760 /sandbox/resolver/cache

COPY cacerts/*.pem /cacerts/

COPY scripts/*.sh /

RUN chmod 755 /*.sh && \
    ln -s /sandbox/resolver/ScaResolver /usr/local/bin/ScaResolver && \
    ln -s /sandbox/resolver/ImageResolverCli /usr/local/bin/ImageResolverCli

WORKDIR /sandbox/resolver

ENTRYPOINT ["/entrypoint.sh"]


##########################################################################
FROM alpine:latest AS extracted-musl
ARG CONFIG_DIR=default-config
WORKDIR /sandbox/resolver
ADD  https://sca-downloads.s3.amazonaws.com/cli/latest/ScaResolver-musl64.tar.gz /sandbox/resolver
RUN tar -xzf ScaResolver-musl64.tar.gz && \
    rm -f ScaResolver-*.tar.gz
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/
RUN chmod -R 750 /sandbox/resolver


##########################################################################
FROM alpine:latest AS extracted-linux
ARG CONFIG_DIR=default-config
WORKDIR /sandbox/resolver
ADD https://sca-downloads.s3.amazonaws.com/cli/latest/ScaResolver-linux64.tar.gz /sandbox/resolver
RUN tar -xzf ScaResolver-linux64.tar.gz && \
    rm -f ScaResolver-*.tar.gz
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/
RUN chmod -R 750 /sandbox/resolver


##########################################################################
FROM base-config AS resolver-alpine

COPY --from=extracted-musl /sandbox/resolver/* /sandbox/resolver/

RUN apk add -q libstdc++ bash && \
    [[ "$(getent group ${GROUP_ID})" = "" ]] && { addgroup -g ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    addgroup root $TARGET_GROUP && \
    [[ "$(getent passwd ${USER_ID})" = "" ]] && {  adduser -D -s /sbin/nologin -g $TARGET_GROUP resolver ; TARGET_NAME=resolver ; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:$TARGET_GROUP /sandbox/output /sandbox/input /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}


##########################################################################
FROM base-config AS resolver-debian

COPY --from=extracted-linux /sandbox/resolver/* /sandbox/resolver/

RUN apt update && \
    apt install -y ca-certificates && \
    apt clean

SHELL ["/usr/bin/bash", "-c"]

RUN \
    [[ "$(getent group ${GROUP_ID})" = "" ]] && { addgroup --gid ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    adduser root $TARGET_GROUP && \
    [[ "$(getent passwd ${USER_ID})" = "" ]] && { adduser --disabled-password --no-create-home --ingroup sca --disabled-login --uid ${USER_ID} resolver ; TARGET_NAME=resolver; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    chmod -R 750 /sandbox/resolver && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:$TARGET_GROUP /sandbox/output /sandbox/input /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}

##########################################################################
FROM base-config AS resolver-redhat

COPY --from=extracted-linux /sandbox/resolver/* /sandbox/resolver/

RUN \
    [[ $(command -v microdnf) != "" ]] && { microdnf install -y --nodocs shadow-utils which ; microdnf clean all ; } || : && \
    [[ "$(getent group ${GROUP_ID})" = "" ]] && { groupadd --gid ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    [[ "$(getent passwd ${USER_ID})" = "" ]] && { adduser --no-create-home -G $TARGET_GROUP resolver ; TARGET_NAME=resolver; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    usermod -a -G $TARGET_GROUP root && \
    chmod -R 750 /sandbox/resolver && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:$TARGET_GROUP /sandbox/output /sandbox/input /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}

##########################################################################
FROM base-config AS resolver-amazon

COPY --from=extracted-linux /sandbox/resolver/* /sandbox/resolver/

RUN yum install -y shadow-utils which && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    groupadd --gid ${GROUP_ID} sca && \
    adduser --no-create-home -G sca resolver && \
    usermod -G sca root && \
    chmod -R 750 /sandbox/resolver && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:sca /sandbox/output /sandbox/input /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}
