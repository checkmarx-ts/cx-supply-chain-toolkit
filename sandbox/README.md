# SCAResolver Sandboxed Container

The image here is intended to build a container derived from a base container that is a build image set in a CI/CD environment.  The created container will have SCAResolver installed and will be used to execute dependency resolution.

Executing dependency resolution should be done in a sandbox given that there are a few scenarios where the build can execute potentially untrusted code:

* As part of the build scripting.
* Execution of installation scripts during package installation.

Not all build systems have the potential to execute code. Executing dependency resolution in a sandbox is a best practice due to the recently proliferation of open-source supply-chain attacks.

The successful use of this container to sandbox dependency resolution is limited to what is enable or exposed in the base image.  Nothing is foolproof.

# Supported Images

The `Dockerfile` is a multi-stage build that uses stage names to specify the correct image build.  The stage names are intended to align with popular images used in build platforms.  Currently, the stages available for base image alignment:

* resolver-alpine
* resolver-ubuntu
* resolver-redhat
* resolver-amazon

# How the Sandboxing Works

Containers executed from a sandbox image run as the user `resolver` that belongs to the group `sca`.  The user `resolver` has no privileges other than what are assigned at the time the image is built.

Several directories are created as part of the image build so that they can be mapped to an external volume:

|Directory|Comments|
|-|-|
|`/scalogs`| Used to write SCAResolver logs. |
|`/code`| This is where the code should exist that needs to be scanned. |
|`/output`| This is the directory where SCAResolver results file `sca-results.json` will be written.|

Performing a `docker run` for an SCAResolver image passes the arguments through to SCAResolver.  You can modify the `default-config/Configuration.yml` to set default options for SCAResolver.  In the [How to Build](#how-to-build) section, a method is described to allow you to choose a non-default `Configuration.yml` at the time of build.

There are various ways of mapping local disk volumes to the container's directories.  One method is to provide the mapping from `docker run` such as:

`docker run --rm -it -v /my-log-path:/scalogs -v .:/code -v ./sca-results:/output my-scaresolver-tag {SCAResolver args...}`

## **CAUTION**

Any file, environment variable, or network destination that can be accessed from the running container can be potentially accessed during dependency resolution.  This means environment variables or mapped secrets can be exfiltrated or exploited for use in accessing internal systems.

Running SCAResolver in `offline` mode can perform dependency resolution without generally needing any credentials or other sensitive information available.  If your build environment requires credentials to resolve dependencies, please consult with Checkmarx Professional Services.

### *CAVEAT* 
Exploitable Path currently requires SAST credentials, which could potentially be obtained during a build script execution.  Passed in the command line parameters, this should not be easy to obtain.  If provided in the `Configuration.yml`, they are trivial to obtain. **Verification is TBD.**


# How to Build

The first step is to determine if your base image is compatible with one of the stage targets.  If your build image won't work with one of the aligned stages, please consult Checkmarx Professional Services if you need help to add a compatible build stage.  

If you wish to attempt to add your own build stage, please study the sandbox `Dockerfile` to create your own stage. 

The general build pattern is:

```
docker build -t {your tag} --build-arg BASE={tag for your build image} --build-arg CONFIG_DIR={directory for your custom configuration} --target=resolver-{compatible stage} .

```

## Obtain the SCAResolver Download

The `scaresolver-bin` folder defaults to empty.  It is intended that you obtain the Linux and Alpine Linux versions of SCAResolver from [the SCAResolver download page](https://checkmarx.com/resource/documents/en/34965-19197-checkmarx-sca-resolver-download-and-installation.html).

If the SCAResolver tarballs are not provided, the image build will fail.

## Base Image

The build argument `BASE` is optional and will default to `alpine:latest` if not provided.  The `BASE` argument should be the tag of a container image that you have defined as appropriate for the `--target` build stage .  

Your base image should contain all required build tooling that would be used in resolving dependencies when run against a project that would normally build with that base image.

## Custom Configs

The build argument `CONFIG_DIR` is optional and will default to `default-config` if not provided.  You can create your custom configuration by creating a new directory and copying the contents of `default-config` to initialize the configuration artifacts.  You can then modify the configuration artifacts to fit the configuration needed by the generated image.

## CA Certificates

The `cacerts` directory contains Amazon AWS Root CA certs that are used as the CA certificate for Checkmarx services.  You can add your own PEM encoded CA certificates in this directory and it will be included as a trusted CA by the image.

If desired, you can remove the AWS CA files as long as there is at least one PEM encoded certificate left in the directory during image build.

# Execution Patterns

SCAResolver can execute in an `online` mode where credentials for the SCA instance are provided in the command line.  **Is this a problem?**

offline and upload
