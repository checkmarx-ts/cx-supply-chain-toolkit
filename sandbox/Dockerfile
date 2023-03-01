ARG BASE=alpine:latest

FROM ${BASE} AS base-config

RUN mkdir -p /sandbox/scalogs && \
    chmod -R 730 /sandbox/scalogs && \
    mkdir -p /sandbox/code && \
    chmod -R 750 /sandbox/code && \
    mkdir -p /sandbox/output && \
    chmod -R 730 /sandbox/output 

COPY cacerts/*.pem /cacerts/

COPY entrypoint.sh /

RUN chmod 755 /entrypoint.sh

WORKDIR /sandbox/resolver

ENTRYPOINT ["/entrypoint.sh"]


ARG CONFIG_DIR=default-config
FROM base-config AS resolver-alpine
ADD scaresolver-bin/ScaResolver-musl64.tar.gz /sandbox/resolver
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/

RUN apk add -q libstdc++ && \
    addgroup -g 4096 sca && \
    addgroup root sca && \
    adduser -D -G sca -s /sbin/nologin -g resolver resolver && \
    chmod -R 750 /sandbox/resolver && \
    rm -f /sandbox/resolver/Configuration.ini && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    chown -R root:sca /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER resolver



FROM base-config AS resolver-ubuntu
ADD scaresolver-bin/ScaResolver-linux64.tar.gz /sandbox/resolver
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/

RUN addgroup sca && \
    adduser root sca && \
    adduser --disabled-password --no-create-home --ingroup sca --disabled-login resolver && \
    chmod -R 750 /sandbox/resolver && \
    rm -f /sandbox/resolver/Configuration.ini && \
    apt update && apt install -y ca-certificates && \
    apt clean && \
    for cert in $(ls /cacerts); do cat /cacerts/$cert >> /etc/ssl/certs/ca-certificates.crt; done && \
    chown -R root:sca /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER resolver

FROM base-config AS resolver-redhat
ADD scaresolver-bin/ScaResolver-linux64.tar.gz /sandbox/resolver
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/

RUN [[ $(command -v microdnf > /dev/null 2>&1) -eq 0 ]] && microdnf install -y --nodocs shadow-utils || : && \
    [[ $(command -v microdnf > /dev/null 2>&1) -eq 0 ]] && microdnf clean || : && \
    groupadd sca && \
    adduser --no-create-home -G sca resolver && \
    usermod -G sca root && \
    chmod -R 750 /sandbox/resolver && \
    rm -f /sandbox/resolver/Configuration.ini && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    chown -R root:sca /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER resolver

FROM base-config AS resolver-amazon
ADD scaresolver-bin/ScaResolver-linux64.tar.gz /sandbox/resolver
COPY ${CONFIG_DIR}/Configuration.yml /sandbox/resolver/

RUN yum install -y shadow-utils && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    groupadd sca && \
    adduser --no-create-home -G sca resolver && \
    usermod -G sca root && \
    chmod -R 750 /sandbox/resolver && \
    rm -f /sandbox/resolver/Configuration.ini && \
    cp /cacerts/* /etc/pki/ca-trust/source/anchors/ && \
    update-ca-trust extract && \
    chown -R root:sca /sandbox/output /sandbox/code /sandbox/scalogs /sandbox/resolver

USER resolver
