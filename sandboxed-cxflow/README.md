# Sandboxed CxFlow

This is a re-built CxFlow image that follows the release configuration of the official CxFlow image.  The main purpose
of this image is to allow the execution of SCAResolver in a (mostly) sandboxed, customer-defined environment.

This is a work in progress.

# Docker in Docker

This image works by invoking Docker inside the Docker container.  This means the deployment options may be somewhat limited given that
running Docker inside a Docker container has to be done with the correct deployment environment.

## CI/CD Pipeline Deployment

Compatibility scenarios are TBD.  In most build pipeline tools, the containers running each stage can invoke Docker.

## Container Orchestrators and Hosting Infrastructure

Compatibility with services such as AWS ECS is TBD.  These may not be a viable deployment solution due to the
privileges needed for Docker in Docker execution.

## Instance Deployment

The testing for this was mostly done with deployment on a compute instance.  Deployment pre-requisites are:

* Linux instance with a kernel >= 5.12
* [Sysbox](https://github.com/nestybox/sysbox) installed

Running the container with the `--privileged` flag may be an option to avoid the need for Sysbox and allow it to run on Linux kernels
with versions prior to 5.12.  This is TBD.

### Installing Sysbox

This installation was performed on an Ubuntu Linux install.  [Sysbox](https://github.com/nestybox/sysbox) provides a [list of
compatible Linux distributions](https://github.com/nestybox/sysbox/blob/master/docs/distro-compat.md#supported-linux-distros) that may be an
alternative to using Ubuntu. The [Sysbox](https://github.com/nestybox/sysbox) installation guide does give instructions for
[installing Shitfs](https://github.com/nestybox/sysbox/blob/master/docs/distro-compat.md#shiftfs-requirement) to support Linux kernel versions
prior to 5.12.  This is not a tested scenario.

To install Sysbox on Ubuntu, the following commands are executed:

```
wget https://downloads.nestybox.com/sysbox/releases/v0.5.2/sysbox-ce_0.5.2-0.linux_amd64.deb
apt install -y jq docker.io ./sysbox-ce_0.5.2-0.linux_amd64.deb
```


Running CxFlow is performed with this command:

```
docker run --runtime=sysbox-runc -d <the CxFlow image tag>
```

If the `--runtime=sysbox-runc` option is not included and not using the `--privileged` flag, the image will encounter errors when attempting to invoke Docker.

# CxFlow Image Compatibility

All the existing Spring Boot facilities for configuring CxFlow via environment variables work with this image.  Using this image
in place of the official CxFlow image is compatible as long as there is no need to execute SCAResolver.

If using SCAResolver, there is more configuration needed.  The container will actively attempt to prevent you from configuring the `SCA_PATH_TO_SCA_RESOLVER` option, 
providing the path on the command line or setting it in the YAML configuration.  SCAResolver has been replaced in this image with an mediation script that invokes SCAResolver
in an appropriate container image.

This image can be used for web hook or command line CxFlow execution.

# Environment Variables: Options for the Image

This image supports non-CxFlow environment variables that change how it operates at runtime.

## `JAVA_OPTS`
The default value for this environment variable is `-Xms512m -Xmx2048m`.  This variable can be used to pass options to the Java runtime
prior to executing the CxFlow jar.

## `JAVA_PROPS`
The default value for this environment variable is `-Djava.security.egd=file:/dev/./urandom`.  This is passed to the Java runtime after `JAVA_OPTS` and before the CxFlow
jar is executed.  

## `SPRING_PROPS`
The default value for this environment variable is `-Dspring.profiles.active=web`.  This is passed to the Java runtime after `JAVA_PROPS` and before the
CxFlow jar is executed.  CxFlow has embedded profiles that can be used as a basic set of configurations.  Most of them are outdated; the `web` profile
usually causes fewer configuration issues.  These are not documented in the CxFlow documentation, so it is best to leave this as-is unless
advised to do otherwise.

## `NO_DOCKERD`

Set the environment variable `NO_DOCKERD` (no value is required) to prevent starting `dockerd` on startup. 
Attempting to execute SCAResolver without `dockerd` running will result in an error


## `CXFLOW_ALT_JAR_URL`

If the environment variable `CXFLOW_ALT_JAR_URL` contains a URL to a CxFlow jar, that jar will be downloaded and executed instead of
the CxFlow jar embedded in the container.


## `CXFLOW_JAR_SHA256`

Set this value with a SHA-256 hash that is expected to match the CxFlow jar.  If replacing the CxFlow jar using `CXFLOW_ALT_JAR_URL`,
validating the correct hash value before execution is highly encouraged.  If the SHA-256 of the CxFlow jar to be executed does not match
the provided SHA-256, the jar will not be executed.


## `CXFLOW_YAML_URL`

If the environment variable `CXFLOW_YAML_URL` contains a URL to a CxFlow YAML configuration file, it will be downloaded and set
as the CxFlow configuration.


## `DISPATCHER_YAML_URL`

If the environment variable `DISPATCHER_YAML_URL` contains a URL to a Dispatcher YAML configuration file, it will be downloaded and set
as the Dispatcher configuration.


# SCAResolver Dispatcher

The exact description of the Dispatcher is TBD.  The basic idea is to execute SCAResolver in a mostly sandboxed execution environment.  The execution environment
could be a customized build environment.

The execution environment can be defined as:

* default - The default image, runtime parameters, environment variables, and SCAResolver parameters used if no runtime environment can be determined
* tag - The image, runtime parameters, environment variables, and SCAResolver parameters used if a project has a matching tag

Project tags are obtained from a config-as-code file in the root of the repository (not the CxFlow config as code file).  Future enhancements may allow this to be resolved from
project tags found via the SCA API.

## Dispatcher Configuration

This is presented in YAML.  Environment variables that follow the Spring Boot convention can be used instead of a YAML file.

```yaml

docker:
    login:
        <server name>:
            username:
            password:
    ...
        <server name>:
            username:
            password:


resolver-images:
    default-image:
        container: <image>:<tag>
        container-ttl: 15m
        exec-timeout: 10m
        exec-env:
            <variable>: value
            ...
            <variable>: value
        exec-params:
            - <sca resolver param>
            ...
            - <sca resolver param>
    project-tags:
        <tag>: 
            container: <image>:<tag>
            container-ttl: 15m
            exec-timeout: 10m
            exec-env:
                <variable>: value
                ...
                <variable>: value
            exec-params:
                - <sca resolver param>
                ...
                - <sca resolver param>
    ...
        <tag>: 
            container: <image>:<tag>
            container-ttl: 15m
            exec-timeout: 10m
            exec-env:
                <variable>: value
                ...
                <variable>: value
            exec-params:
                - <sca resolver param>
                ...
                - <sca resolver param>
```




