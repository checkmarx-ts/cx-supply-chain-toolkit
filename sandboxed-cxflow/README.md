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

### Logging

CxFlow logs to the console to maintain running compatibility with the official CxFlow image.  Any dispatcher operations are logged in files found on the 
container in the directory `/var/log/dispatcher`.  The use of logging files for the dispatcher is to avoid the console logs from being corrupted
by spontaneous log emissions from the dispatcher.

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


## `DEBUG`

If the variable `DEBUG` exists in the environment, debug logging output will be enabled.


# SCAResolver Dispatcher

The exact description of the Dispatcher is TBD.  The basic idea is to execute SCAResolver in a mostly sandboxed execution environment.  The execution environment
could be a customized build environment.

The execution environment can be defined as:

* default - The default image, runtime parameters, environment variables, and SCAResolver parameters used if no runtime environment can be determined
* tag - The image, runtime parameters, environment variables, and SCAResolver parameters used if a project has a matching tag

Project tags are obtained from a config-as-code file in the root of the repository (not the CxFlow config as code file).  Future enhancements may allow this to be resolved from
project tags found via the SCA API.

## Dispatcher Configuration

Configuration can be represented by both YAML and Environment variables.  The first YAML file found in `$(pwd)/yaml` when the Dispatcher starts is used
as the configuration file.  The configuration is evaluated in the following order of precedence:

1. Environment variables
2. YAML configuration

An example of the complete YAML configuration can be observed below:

```yaml

docker:
    login:
        registry-1.docker.io:
            username: XXXXXXXXX
            password: XXXXXXXXX
        ...
        ghcr.io:
            username: XXXXXXXXX
            password: XXXXXXXXX

resolver:
    defaults:
        containerttl: 15m
        exectimeout: 10m
        defaulttag: default

    images:
        default:
            container: test:gradle
            containerttl: 5m
            exectimeout: 10m
            execenv:
                FOO: BAZ
            execparams:
                - --log-level=Verbose
        node: 
            container: test:node-linux
            execenv:
                FOO: BAR
            envpropagate:
                - MY_ENVIRONMENT_VARIABLE1
                - MY_ENVIRONMENT_VARIABLE2

```


### Section: `docker`

This section is optional.  It is intended to provide defaults for Docker invocations.

#### `docker.login`

This section is a list of container repositories where a `docker login` command will be executed on CxFlow startup.  If the images tags
configured in the `resolver` section are not stored in the default Docker public repository, configure the repositories here.

Multiple image repositores can be defined using multiple entries under `docker.login`.


```yaml

docker:
    login:
        registry-1.docker.io:
            username: XXXXXXXXX
            password: XXXXXXXXX
        ghcr.io:
            username: XXXXXXXXX
            password: XXXXXXXXX
        my-host.com:
            username: XXXXXXXXX
            password: XXXXXXXXX
```

Dashes in hostnames can be represented in environment variable names with a double underscore.  Underscores are not valid in DNS hostnames and are therefore not supported.

The above example of the `docker.login` YAML has the equivalent environment variables:

```
DOCKER_LOGIN_HUB_DOCKER_IO_USERNAME=XXXX
DOCKER_LOGIN_HUB_DOCKER_IO_PASSWORD=XXXX
DOCKER_LOGIN_MY__HOST_COM_USERNAME=XXXX
DOCKER_LOGIN_MY__HOST_COM_PASSWORD=XXXX
```


### Section: `resolver`

This section is used to define parameters for SCAResolver invocation.

#### `resolver.twostage`

This is optional, defaults to `true`.

If `true`, an `online` SCAResolver scan will be split into two stages:

* The first stage is an `offline` scan.  When invoking the offline scan, credentials for the SCA server are stripped from the command.  This executes the dependency
resolution without leaving credentials exposed to any scripts that execute as part of the dependency resolution.
* The second stage is an `upload` where the dependency resolution results are uploaded to the SCA server.

If set to `false`, an `online` scan will be invoked in a single step.


#### `resolver.defaults`

This section is optional; it allows for overriding the hard-coded default values if desired.

The timespan values here can be represented by simple value strings with numeric indicators indicating time units such as `h` for hours, `m` for 
minutes, and `s` for seconds.  Example:

`2h15m30s` means 2 hours, 15 minutes, and 30 seconds

`15m` means 0 hours, 15 minutes, and 0 seconds

An example of the `resolver.defaults` section can be observed below:

```yaml

resolver:
    defaults:
        containerttl: 15m
        exectimeout: 10m
        defaulttag: default
        delete: False

```

`resolver.defaults.containerttl` - If not provided, this defaults to 1 hour.  This is the length of time a container image will be used after the
initial `docker pull` command is executed to download the image.  This allows updated images to be retrieved without the need to stop CxFlow.

`resolver.defaults.exectimeout` - If not provided, this defaults to 30 minutes.  This is the amount of time CxFlow will allow the SCAResolver
image to execute before killing it and assuming failure.

`resolver.defaults.defaulttag` - If not provided, this defaults to the value of `default`.  This is the tag of the image configured in
`resolver.images` used if an unknown tag is requested.

`resolver.defaults.delete` - If not provided, this defaults to the value of `True`.  Setting this to `False` will prevent the container image created
for the scan from being deleted.

The above example of the `resolver.defaults` YAML has the equivalent environment variables:

```
RESOLVER_DEFAULTS_CONTAINTERTTL=15m
RESOLVER_DEFAULTS_EXECTIMEOUT=10m
RESOLVER_DEFAULTS_DEFAULTTAG=default
RESOLVER_DEFAULTS_DELETE=False
```

#### `resolver.images`

This section is where the image parameters are set for a container matching a tag that indicates which container image to
use when invoking SCAResolver.

Each dictionary of key/value pairs configured under the `resolver.images` uses the key value as the image tag.  An example of a configuraton
for images tagged `default` and `node`.  The containers defined would be instances of [the SCAResolver sandbox](../sandbox) image derived
from an appropriate build environment base image.

In each of the sections, the `containerttl` and `exectimeout` values are optional.  If not provided, the corresponding values from the 
`resolver.defaults` section will be used.


```yaml

resolver:
    images:
        default:
            container: test:gradle
            containerttl: 5m
            exectimeout: 10m
            execenv:
                FOO: BAZ
            execparams:
                - --log-level=Verbose
        node: 
            container: test:node-linux
            execenv:
                FOO: BAR
            envpropagate:
                - MY_ENVIRONMENT_VARIABLE1
                - MY_ENVIRONMENT_VARIABLE2

```


`resolver.images.<tag>.container` - Required.  The container image tag name associated with the configuration tag that will be resolved as
part of the CxFlow scan execution.  

`resolver.images.<tag>.containerttl` - Optional.  Uses the corresponding value from `resolver.defaults` if not provided.

`resolver.images.<tag>.exectimeout` - Optional.  Uses the corresponding value from `resolver.defaults` if not provided.

`resolver.images.<tag>.execenv` - Optional.  A dictionary of key/value pairs that are emitted in the environment when the container image is executed.  Entries
with key values that match keys defined in `resolver.images.<tag>.envpropagate` will have the value overwritten by the value found in the propagated environment
value.

`resolver.images.<tag>.execparams` - Optional.  An array of values passed to SCAResolver at the end of all other parameters needed to control the
execution of SCAResolver.  The values here are mainly intended to pass configuration values to dependency resolution tools invoked by SCAResolver.  Passing other values
to SCAResolver may cause operational conflicts.

`resolver.images.<tag>.envpropagate` - Optional.  An array of names of environment variables in the CxFlow environment that will be propagated as-is to the 
executing image environment.

`resolver.images.<tag>.dockerparams` - Optional. An a key/value dictionary that follows the `**kwargs` key/value pairs supported in the [Docker Python API](https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run) `run` method.


The above example of the `resolver.images` YAML has the equivalent environment variables:

```
RESOLVER_IMAGES_DEFAULT_CONTAINER=test:gradle
RESOLVER_IMAGES_DEFAULT_CONTAINERTTL=5m
RESOLVER_IMAGES_DEFAULT_EXECTIMEOUT=10m
RESOLVER_IMAGES_DEFAULT_EXECENV_FOO=BAZ
RESOLVER_IMAGES_DEFAULT_EXECPARAMS_1=--log-level=Verbose
RESOLVER_IMAGES_NODE_CONTAINER=test:node-linux
RESOLVER_IMAGES_NODE_EXECENV_FOO=BAR
RESOLVER_IMAGES_NODE_ENVPROPAGATE_1=MY_ENVIRONMENT_VARIABLE1
RESOLVER_IMAGES_NODE_ENVPROPAGATE_2=MY_ENVIRONMENT_VARIABLE2
```

