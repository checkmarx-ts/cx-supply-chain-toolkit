ARG BASE=alpine:latest

##########################################################################
FROM ${BASE} AS base-config
USER root

RUN mkdir -p /sandbox/scalogs && \
    chmod -R 730 /sandbox/scalogs && \
    mkdir -p /sandbox/input && \
    chmod -R 750 /sandbox/input && \
    mkdir -p /sandbox/input_sandbox && \
    chmod -R 770 /sandbox/input_sandbox && \
    mkdir -p /sandbox/output && \
    chmod -R 730 /sandbox/output && \
    mkdir -p /sandbox/report && \
    chmod -R 730 /sandbox/report && \
    mkdir -p /sandbox/resolver/cache && \
    chmod -R 760 /sandbox/resolver/cache

COPY cacerts/*.pem /cacerts/

COPY scripts/*.sh /

RUN chmod 755 /*.sh && \
    ln -s /sandbox/resolver/ScaResolver /usr/local/bin/ScaResolver && \
    ln -s /sandbox/resolver/ImageResolverCli /usr/local/bin/ImageResolverCli

WORKDIR /sandbox/input_sandbox


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
FROM alpine:latest AS cxone-extracted-linux
WORKDIR /sandbox/cxonecli
ADD https://github.com/Checkmarx/ast-cli/releases/latest/download/ast-cli_linux_x64.tar.gz /sandbox/cxonecli
RUN tar -xzf ast-cli_linux_x64.tar.gz && \
    rm -f ast-cli_linux*.tar.gz
RUN chmod -R 750 /sandbox/cxonecli


##########################################################################
FROM base-config AS resolver-alpine-bare
ARG GROUP_ID=1000
ARG USER_ID=1000
USER root

COPY --from=extracted-musl /sandbox/resolver/* /sandbox/resolver/
COPY --from=cxone-extracted-linux /sandbox/cxonecli/* /sandbox/cxonecli/

RUN apk add -q libstdc++ bash && \
    [[ "$(getent group ${GROUP_ID})" = "" ]] && { addgroup -g ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    addgroup root $TARGET_GROUP && \
    [[ "$(getent passwd ${USER_ID})" = "" ]] && {  adduser -u ${USER_ID} -D -s /sbin/nologin -G $TARGET_GROUP resolver ; TARGET_NAME=resolver ; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:$TARGET_GROUP /sandbox

FROM resolver-alpine-bare AS resolver-alpine
ARG GROUP_ID=1000
ARG USER_ID=1000
USER  ${USER_ID}:${GROUP_ID}
ENTRYPOINT ["/entrypoint.sh"]


##########################################################################
FROM base-config AS resolver-debian-bare
ARG GROUP_ID=1000
ARG USER_ID=1000
USER root

COPY --from=extracted-linux /sandbox/resolver/* /sandbox/resolver/
COPY --from=cxone-extracted-linux /sandbox/cxonecli/* /sandbox/cxonecli/

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    ln -s $(which bash) /usr/bin/bsh && \
    apt-get clean

SHELL ["/usr/bin/bsh", "-c"]

RUN \
    [[ "$(getent group ${GROUP_ID})" = "" ]] && { addgroup --gid ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    adduser root $TARGET_GROUP && \
    [[ "$(getent passwd ${USER_ID})" = "" ]] && { adduser --disabled-password --ingroup sca --disabled-login --uid ${USER_ID} resolver ; TARGET_NAME=resolver; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    chmod -R 750 /sandbox/resolver && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:$TARGET_GROUP /sandbox


FROM resolver-debian-bare AS resolver-debian
ARG GROUP_ID=1000
ARG USER_ID=1000
USER  ${USER_ID}:${GROUP_ID}
ENTRYPOINT ["/entrypoint.sh"]




##########################################################################
FROM base-config AS resolver-redhat-bare
ARG GROUP_ID=1000
ARG USER_ID=1000
USER root

COPY --from=extracted-linux /sandbox/resolver/* /sandbox/resolver/
COPY --from=cxone-extracted-linux /sandbox/cxonecli/* /sandbox/cxonecli/

RUN \
    [[ $(command -v microdnf) != "" ]] && { microdnf install -y --nodocs shadow-utils which ; microdnf clean all ; } || : && \
    [[ "$(getent group ${GROUP_ID})" = "" ]] && { groupadd --gid ${GROUP_ID} sca ; TARGET_GROUP=sca ; } || TARGET_GROUP=$(getent group ${GROUP_ID} | cut -d ':' -f1) && \
    [[ "$(getent passwd ${USER_ID})" = "" ]] && { adduser -G $TARGET_GROUP resolver ; TARGET_NAME=resolver; } || TARGET_NAME=$(getent passwd ${USER_ID} | cut -d ':' -f1) && \
    usermod -a -G $TARGET_GROUP root && \
    chmod -R 750 /sandbox/resolver && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:$TARGET_GROUP /sandbox


FROM resolver-redhat-bare AS resolver-redhat
ARG GROUP_ID=1000
ARG USER_ID=1000
USER  ${USER_ID}:${GROUP_ID}
ENTRYPOINT ["/entrypoint.sh"]


##########################################################################
FROM base-config AS resolver-amazon-bare
ARG GROUP_ID=1000
ARG USER_ID=1000
USER root

COPY --from=extracted-linux /sandbox/resolver/* /sandbox/resolver/
COPY --from=cxone-extracted-linux /sandbox/cxonecli/* /sandbox/cxonecli/

RUN yum install -y shadow-utils which && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    groupadd --gid ${GROUP_ID} sca && \
    adduser -G sca resolver && \
    usermod -G sca root && \
    chmod -R 750 /sandbox/resolver && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    echo IMAGE BUILD UID:GID: $TARGET_NAME:$TARGET_GROUP as $USER_ID:$GROUP_ID && \
    chown -R root:sca /sandbox

FROM resolver-amazon-bare AS resolver-amazon
ARG GROUP_ID=1000
ARG USER_ID=1000
USER  ${USER_ID}:${GROUP_ID}
ENTRYPOINT ["/entrypoint.sh"]

