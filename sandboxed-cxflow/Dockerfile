FROM amazoncorretto:11-al2022-jdk

ENV JAVA_OPTS="-Xms512m -Xmx2048m"
ENV JAVA_PROPS="-Djava.security.egd=file:/dev/./urandom"
ENV SPRING_PROPS="-Dspring.profiles.active=web"

RUN yum install -y shadow-utils which unzip wget git docker && \
    # amazon-linux-extras install -y docker && \
    systemctl enable containerd && \
    systemctl enable docker && \
    yum clean all && \
    rm -rf /var/cache/yum 

RUN \
    adduser --no-create-home -G docker cxflow && \
    usermod -G cxflow root && \
    mkdir /app && \
    chown root:cxflow /app && \
    chmod 770 /app && \
    mkdir /yaml && \
    chown root:cxflow /yaml && \
    chmod 770 /yaml && \
    mkdir -p /resolver/yaml && \
    chown -R root:cxflow /resolver && \
    chmod -R 770 /resolver && \
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


WORKDIR /app
USER cxflow

CMD ["--web"]
ENTRYPOINT ["/app/entrypoint.sh"]
