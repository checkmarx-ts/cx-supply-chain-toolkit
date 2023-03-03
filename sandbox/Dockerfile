ARG BASE=alpine:latest

FROM ${BASE} AS base-config

ARG CONFIG_DIR=default-config
ARG GROUP_ID=1000
ARG USER_ID=1000

RUN mkdir -p /sandbox/scalogs && \
    chmod -R 730 /sandbox/scalogs && \
    mkdir -p /sandbox/code && \
    chmod -R 750 /sandbox/code && \
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


ARG CONFIG_DIR=default-config
FROM base-config AS base-musl
ADD  https://sca-downloads.s3.amazonaws.com/cli/latest/ScaResolver-musl64.tar.gz /sandbox/resolver
RUN tar -xzf ScaResolver-musl64.tar.gz && \
    rm -f ScaResolver-*.tar.gz && \
    chmod -R 750 /sandbox/resolver
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/


FROM base-config AS base-linux
ADD https://sca-downloads.s3.amazonaws.com/cli/latest/ScaResolver-linux64.tar.gz /sandbox/resolver
RUN [[ $(tar -xzf ScaResolver-linux64.tar.gz) -eq 0 ]] && : || rm -f ScaResolver-linux64.tar.gz && \
    chmod -R 750 /sandbox/resolver

    
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/

FROM base-linux AS base-linux-yum-tar

RUN yum install -y tar gzip && \
    tar -xzf ScaResolver-linux64.tar.gz && \
    rm -f ScaResolver-*.tar.gz


FROM base-musl AS resolver-alpine

RUN apk add -q libstdc++ bash && \
    getent group ${GROUP_ID} > /dev/null && \
    [[ $? -ne 0 ]] && { addgroup -g ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    addgroup root $TARGET_GROUP && \
    getent passwd ${USER_ID} > /dev/null && \
    [[ $? -ne 0 ]] && {  adduser -D -G $TARGET_GROUP -s /sbin/nologin -g resolver resolver ; TARGET_NAME=resolver ; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    chown -R root:$TARGET_GROUP /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}


FROM base-linux AS resolver-debian

RUN apt update && \
    apt install -y ca-certificates && \
    apt clean

SHELL ["/usr/bin/bash", "-c"]

RUN getent group ${GROUP_ID} > /dev/null && \
    [[ $? -ne 0 ]] && { addgroup --gid ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    adduser root $TARGET_GROUP && \
    getent passwd ${USER_ID} > /dev/null && \
    [[ $? -ne 0 ]] && { adduser --disabled-password --no-create-home --ingroup sca --disabled-login --uid ${USER_ID} resolver ; TARGET_NAME=resolver; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    chmod -R 750 /sandbox/resolver && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    chown -R root:$TARGET_GROUP /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}

FROM base-linux AS resolver-redhat

RUN [[ $(command -v microdnf > /dev/null 2>&1) -eq 0 ]] && microdnf install -y --nodocs shadow-utils || : && \
    [[ $(command -v microdnf > /dev/null 2>&1) -eq 0 ]] && microdnf clean || : && \
    groupadd --gid ${GROUP_ID} sca && \
    adduser --no-create-home -G sca resolver && \
    usermod -G sca root && \
    chmod -R 750 /sandbox/resolver && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    chown -R root:sca /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}

FROM base-linux-yum-tar AS resolver-amazon

RUN yum install -y shadow-utils && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    groupadd --gid ${GROUP_ID} sca && \
    adduser --no-create-home -G sca resolver && \
    usermod -G sca root && \
    chmod -R 750 /sandbox/resolver && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    chown -R root:sca /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER  ${USER_ID}:${GROUP_ID}
