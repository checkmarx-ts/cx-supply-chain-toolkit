FROM amazoncorretto:11-al2022-jdk

ENV JAVA_OPTS="-Xms512m -Xmx2048m"
ENV JAVA_PROPS="-Djava.security.egd=file:/dev/./urandom"
ENV SPRING_PROPS="-Dspring.profiles.active=web"

RUN yum install -y shadow-utils which unzip wget git docker sudo passwd pip && \
    yum clean all && \
    rm -rf /var/cache/yum

COPY etc/ /etc/

RUN \
    adduser -G docker cxflow && \
    usermod -G cxflow root && \
    passwd -d cxflow && \
    mkdir /app && \
    mkdir -p /var/log/docker && \
    chown root:docker /var/log/docker && \
    chmod g+w /var/log/docker && \
    chown root:cxflow /app && \
    chmod 770 /app && \
    mkdir -p /var/log/dispatcher && \
    chown root:cxflow /var/log/dispatcher && \
    chmod 770 //var/log/dispatcher && \
    mkdir /yaml && \
    chown root:cxflow /yaml && \
    chmod 770 /yaml && \
    mkdir -p /dispatcher/yaml && \
    chown -R root:cxflow /dispatcher && \
    chmod -R 770 /dispatcher && \
    umask 0057

COPY --from=checkmarx/cx-flow:latest /app/cx-flow.jar /stage/

RUN unzip -d /stage /stage/cx-flow.jar META-INF/build-info.properties && \
    CXFLOW_VERSION=$(cat /stage/META-INF/build-info.properties | grep build.version | cut -d '=' -f2) && \
    wget -P /app https://github.com/checkmarx-ltd/cx-flow/releases/download/$CXFLOW_VERSION/cx-flow-$CXFLOW_VERSION-java11.jar && \
    mv /app/cx-flow-$CXFLOW_VERSION-java11.jar /app/cx-flow.jar && \
    rm -rf /stage

COPY --chown=root:cxflow scripts/* /app/

RUN mkdir -p /alt && \
    chown root:cxflow /alt && \
    chmod 770 /alt

COPY --chown=cxflow:cxflow dispatcher/ /dispatcher/

WORKDIR /app
USER cxflow

RUN pip install -r /dispatcher/requirements.txt && \
    rm -f /dispatcher/requirements.txt && \
    rm -rf /dispatcher/tests

CMD ["--web"]
ENTRYPOINT ["/app/entrypoint.sh"]
