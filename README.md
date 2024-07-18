# Checkmarx Supply Chain Toolkit

This repository contains tools for assisting deployment of supply chain vulnerability scanning with Checkmarx products. A complete user manual and downloadable components can be found in the [releases](releases) area to the right side of this page.

## Who Needs the Checkmarx Supply Chain Toolkit?

If you are using [Checkmarx SCA](https://docs.checkmarx.com/en/34965-18662-checkmarx-sca.html) or [Checkmarx One with SCA](https://docs.checkmarx.com/en/34965-67042-checkmarx-one.html) and need to execute [SCA Resolver](https://checkmarx.com/resource/documents/en/34965-19196-checkmarx-sca-resolver.html) in a build pipeline or on demand from a SCM web hook event, the toolkit is for you.

### Quickstart: Pipeline Execution

#### GitHub Workflows

The toolkit is used by these GitHub actions published by
Checkmarx Professional Services:

* For SCA standalone and optionally CxSAST: [CxFlow++ GitHub Action](https://github.com/checkmarx-ts/checkmarx-cxflow-plusplus-github-action)
* For Checkmarx One: [CxOne++ GitHub Action](https://github.com/checkmarx-ts/cxone-plusplus-github-action)

#### Scripted Pipelines

1. Download the latest release of the [build-environment](https://github.com/checkmarx-ts/cx-supply-chain-toolkit/releases/latest/download/build-environment.zip)
2. Expand the build-environment zip in a temporary directory.
3. Use the `download_resolver.sh` script to install the SCA Resolver
executable appropriate for your execution platform.
4. Invoke SCA Resolver directly as part of orchestrating scans or via the Checkmarx One CLI.

#### Invoking in an Existing Container

If your build is performed by executing build tools defined in an existing
container, the toolkit will allow you to create a new container that extends
that existing container with SCA Resolver.  The image can be pre-built and
cached in your container registry or it can be built dynamically using the
`autobuild.sh` script.

Dynamically building an extended container and invoking the SCA Resolver
can be done with the following steps:

1. Download the latest release of the [build-environment](https://github.com/checkmarx-ts/cx-supply-chain-toolkit/releases/latest/download/build-environment.zip)
2. Expand the build-environment zip in a temporary directory.
3. Use the `autobuild.sh` script to build the extended container.
4. Invoke SCA Resolver in the container by:

    a. Mapping the code to scan to the documented paths in the container.
    
    b. Passing arguments to the container on the command line that
    are passed through to the SCA Resolver.

Please see the manual for more information about mapping volumes to the
container.  Note that the Checkmarx One CLI is also installed as part
of the container extension and will invoke the container's SCA Resolver
if given the appropriate parameters.



### Quickstart: Web Hook Execution

This topic is complex and does not have a quick method of
implementation.  Please contact Checkmarx Professional Services for implementation consulting.
