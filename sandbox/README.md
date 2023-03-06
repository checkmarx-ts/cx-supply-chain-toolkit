# SCAResolver Sandboxed Container

The image here is intended to build a container derived from a base container that is a standard or customized build image typically used in a CI/CD pipeline.  The
derived container will contain SCAResolver and have the ability to execute the appropriate package managers needed
for dependency resolution.

The sandboxing is intended to allow SCAResolver to execute a dependency resolution while minimizing the risk of detonating malware payloads found in
untrusted build scripts or package installation scripts. Not all package managers present the risk for detonating malware payloads.

Nothing is foolproof; don't expect that using this container alone hardens your build environment.  A threat modeling exercise should be undertaken to understand
if there are other infrastructure changes needed to properly control what is executed in your build environments.



# Extending Your CI/CD Images

Aside from sandboxing dependency resolution, this image is intended to assist in extending existing CI/CD container images by adding SCAResolver.  This prevents
the need to define your own SCAResolver image for every customized build environment.  The CI/CD images referenced in existing pipelines will already contain
all relevant tools needed for dependency resolution and only need to add SCAResolver.  This image should address common configuration activities that
would be needed to create derived images.

The `Dockerfile` in the root of this repository is multi-stage where stage names specify the correct variation of Linux in the base image.  The stage names are intended to align 
with popular base images used to create build environments.  Currently, the stages available for base image alignment:

* resolver-alpine
* resolver-debian
* resolver-redhat
* resolver-amazon

The stage names are intended to indicate compatibility with configuration steps for the variant of Linux in the root container.

There is currently no support for Windows base images.

## Build Examples

Building with the Gradle 8.0 Alpine with JDK19 container as a base image uses the target `resolver-alpine`:

```
docker build -t <your tag> --build-arg BASE=gradle:8.0-jdk19-alpine --target=resolver-alpine .
```

Building with the Node 19 Alpine container as a base image also uses the target `resolver-alpine`:
```
docker build -t <your tag> --build-arg BASE=node:19-alpine --target=resolver-alpine .
```

Building with the Node 19 Buster (Debian) container as a base image uses the target `resolver-debian`:
```
docker build --progress plain -t test:node-linux --build-arg BASE=node:19-buster --target=resolver-debian .
```

Any image that can be pulled from the public Docker Hub or a docker registry connected via `docker login` can be defined as the base image.  If the wrong
or incompatible stage is specified, the container build will fail.

# Invoking the Sandbox Container

The container can be invoked like SCAResolver from the command line.  Parameters controlling the scan are passed to the container. It is also possible to customize 
the `Configuration.yml` with static parameters that don't need to change with each invoke.

To properly interface with the container, some directories are intended to be mapped to a volume at runtime:

|Directory|Required|Comments|
|-|-|-|
|`/sandbox/scalogs`| No | Used to write SCAResolver logs. |
|`/sandbox/input`| Yes | This is where the input should be mapped for SCAResolver inputs. |
|`/sandbox/output`| Yes | This is the directory where SCAResolver results files will be written.|

Performing a `docker run` for an SCAResolver image passes the arguments through to SCAResolver.  You can modify the `default-config/Configuration.yml` to set default options for SCAResolver.  In the [How to Build](#how-to-build) section, a method is described to allow you to choose a non-default `Configuration.yml` at the time of build.

There are various ways of mapping local disk volumes to the container's directories.  One method is to provide the mapping from `docker run` such as:

`docker run --rm -it -v /my-log-path:/sandbox/scalogs -v .:/sandbox/input -v ./sca-results:/sandbox/output my-scaresolver-tag {SCAResolver args...}`

Note that options passed to SCAResolver that indicate where to place output should be provided with paths prefixed with `/sandbox/output`.  This
is the location in the container where you have mapped a directory for output, so the written output will appear on your mapped volume.

As an example, the `offline` [scan mode example](https://checkmarx.com/resource/documents/en/34965-19199-running-scans-using-checkmarx-sca-resolver.html#UUID-af718204-6dfc-2b27-439e-419b9157d364_id_RunningScansUsingCheckmarxSCAResolver-RunningaScan-OfflineMode) found in the SCAResolver documentation would be executed in a pipeline with a command similar to:

```
docker run -it --rm -v .:/sandbox/input -v ./resolver-output:/sandbox/output -v ./resolver-logs:/sandbox/scalogs <your container tag> offline -n MyApp -r /sandbox/output/results.json

```

# How to Build

The general build pattern is:

```
docker build -t {your tag} --build-arg BASE={tag for your build image} --build-arg CONFIG_DIR={directory for your custom configuration} --target=resolver-{compatible stage} --build-arg USER_ID={your user id} --build-arg GROUP_ID={your group id} .

```

|Argument|Default|Description|
|-|-|-|
|`BASE`|`alpine:latest`|The name of the base image for the container build.|
|`CONFIG_DIR`|`default-config`|The directory where image configuration files are sourced during the build.|
|`USER_ID`|1000|The user id to use when running SCAResolver and creating directories and/or files.|
|`GROUP_ID`|1000|The group id to use when running SCAResolver and creating directories and/or files.|



## `BASE` Build Argument

The build argument `BASE` is optional and will default to `alpine:latest` if not provided.  The `BASE` argument should be the tag of a container image that you have defined as appropriate for the `--target` build stage .  

Your base image should contain all required build tooling that would be used in resolving dependencies when run against a project that would normally build with that base image.

## `CONFIG_DIR` Build Argument

The build argument `CONFIG_DIR` is optional and will default to `default-config` if not provided.  You can create your custom configuration by creating a new directory and copying the contents of `default-config` to initialize the configuration artifacts.  You can then modify the configuration artifacts to fit the configuration needed by the generated image.

## `USER_ID` and `GROUP_ID` Build Arguments

These both default to "1000", which is generally the ID of the first non-system user and group created on a clean Linux system.  Since local directories or files mapped 
to a container maintain the user/group ownership ID and permission bits when mapped, the container's ownership IDs need to match a user and group in the container.
At build time, an existing user/group with the specified IDs will be created if they don't exist.  If your base container already has the user/group with the specified
IDs, those users/groups will be used as the user that executes SCAResolver.

In most build scenarios, these can both remain at the default 1000.  To detect if you need to change these values, you can execute the following 
commands as a stage in your pipeline to[ see the user id and group id](https://www.cyberciti.biz/faq/understanding-etcpasswd-file-format/) values:

```
getent passwd $(whoami)
getent group $(groups)
```



The derived container is not intended to run as root.  After reading the [Notes on Execution](#notes-on-execution) section, you will understand that it is a very bad idea to execute a dependency resolution as root.

## CA Certificates

The `cacerts` directory contains Amazon AWS Root CA certs that are used as the CA certificate for Checkmarx services.  You can add your own PEM encoded CA certificates in this directory and it will be included as a trusted CA by the image.

If desired, you can remove the AWS CA files as long as there is at least one PEM encoded certificate left in the directory during image build.

# Notes on Execution

The concept of the sandbox invocation is to perform the dependency vulnerability scanning in an environment where potentially
sensitive data does not need to exist.  Most dependency resolution tasks do not require any secrets, but this may not be true in your environment.

Any time a dependency resolution is invoked, either as part of the build activities or as a scan via SCAResolver, there is a potential to detonate a malware
payload.


## Threat Scenario Examples

### Build Scripts

Scanning source from a public repository will usually include a build definition that defines the dependencies.  Tools like Gradle require a `build.gradle` file
to define the dependencies and perform the build.  The `build.gradle` file is a Groovy script, therefore Gradle will open it and execute it, which populates the
dependency data in the Gradle memory space.  Since Groovy is a general purpose programming language, `build.gradle` can contain code that, when executed, 
can do anything that the running environment allows.  Usually it 
is a bad idea to run code provided by untrusted third parties.

This is not limited to non-interactive build operations.  For example, opening an untrusted source repository in Visual Studio Code will prompt you to confirm the code in the directory is trusted.  If trust is confirmed, Visual Studio Code will continuously run the build script in the background to keep in sync with the build definition. If
that build script contains malware, it has now executed on the developer's machine.


### Dependent Package Installation

Scanning from a private source repository may also have vectors where malware can be executed.  Some dependency managers download dependent packages and invoke
executable code from the package as part of the package installation.  A common technique for threat actors is to "typo squat" on variations of popular package names
to take advantage of developers inadvertently referencing the threat actor's package instead of the correct package.



## Potential Secrets in a Build Environment

### Environment Variables

It is often the case that CI/CD pipelines inject environment variables into the build environment at the time of the build.  Some of these environment variables contain
sensitive information.  Upon execution of a build or dependency resolution, malware would have access to the environment variables.  Any sensitive data could be
exfiltrated via a simple `curl` execution to post a dump of the environment.  The sensitive credentials could be used to access internal systems that are 
used during the build process.

### Stored Secrets

Stored secrets are also often made available to a running container by the CI/CD pipeline.  These files usually need to be readable by the running build process so that the
secrets can be extracted for use during the build.  Any file in the running container is available to the running build and can be exploited by malware executed
as part of the build.

### Running Processes

Running processes may also be a source of exploitable secrets.  In many cases, the command line parameters used when the process was invoked can be viewed by the build
process running on the same system.  Executing the `ps -a` command on Linux, for example, would be an easy way to view any account credentials passed to a container's
entrypoint.


## Other Potential Threats

If we assume that there is no sensitive data to obtain from malware inadvertently executed as part of the build, there are still other types
of threats that should be considered.  Many of these require the correct design of the build infrastructure to mitigate the threats.

### Network Egress

Many corporate firewalls have network egress controls to block connections outside of the corporate network if the destination is not trusted.  In some cases, 
normal HTTP protocol requests may bypass these blocks.  If an HTTP connection can be originated from the build environment and can reach an endpoint hosted
by a threat actor, it is possible to exfiltrate any data, including source code, available on the system where the build is being performed.

### Internal Network Scanning

As part of the execution of the threat actor's malware payload, the code may probe for vulnerable internal endpoints.  Unprotected corporate endpoints may have
known vulnerabilities that the package code may be able to exploit.

### Persistent Threats

Most CI/CD pipelines fail a build and shut down build resources (such as running container instances) after a defined period of time.  During the time the
build stage resources are alive, the threat actor has a window of time where they are a persistent threat.  In cases where the environment where the build
executed is not shut down with a timeout, this is an opportunity for a threat actor to establish a longer persisting threat.


## SCAResolver Sandbox Execution

To execute the sandbox image, there are some considerations that should be taken.


### SCAResolver `online` vs. `offline` Scans

Running an SCAResolver scan in `online` mode requires that credentials be provided on the command line or in the `Configuration.yml` file.  These can be retrieved
by code invoked as the package manager performs dependency resolution. Avoiding
`online` SCAResolver scans can mitigate the possibility of credential exposure.

Running an SCAResolver scan in `offline` mode does not usually require any credentials or secrets to perform (except when running [Exploitable Path](#scaresolver-exploitable-path-scans)).  Some build environments may require credentials for internal package repositories; if this is the case,
some changes in how the package repository is accessed may need to be considered.

Using a two-step approach, it is possible to first perform an SCAResolver scan in `offline` mode and then execute SCAResolver in `upload` mode.  

During an `offline` scan, it is possible that no credentials would be needed to
perform the dependency resolution.  The container instance running the `offline` scan would tear down at the end, thus discarding changes made by malware.  

The `upload` execution does not perform dependency
resolution, so credentials are not exposed to any potential malware exploits
delivered via dependency resolution.

### SCAResolver Exploitable Path Scans

Exploitable Path scans can be invoked for both `online` and `offline` SCAResolver scans.  In both cases, the SAST system credentials are required to be provided
as command line arguments or in the `Configuration.yml`.  There is currently no way to isolate these credentials from an environment where the dependency
resolution is performed.  This means the SAST credentials are potentially exposed only for cases where Exploitable Path is used.

This may change in the future.  A feature request has been opened to enable retrieving Exploitable Path data in a run context where dependency resolution is not invoked.

