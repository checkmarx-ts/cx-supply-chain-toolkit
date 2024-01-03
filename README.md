# NOTICE
**The tools in this repository should be considered at a level of *Alpha* stability.  Proper testing should be performed before deploying this in a production environment.**

# Checkmarx Supply Chain Toolkit

This repository contains tools for assisting deployment of supply chain vulnerability scanning with Checkmarx products. A complete user manual and downloadable components can be found in the [releases](releases) area to the right side of this page.

# Toolkit Contents Summary


## Build Environment Extension

The `build-extension` toolkit is a `Dockerfile` with associated artifacts that will extend an existing containerized build environment by adding
[SCA Resolver](https://checkmarx.com/resource/documents/en/34965-19196-checkmarx-sca-resolver.html) and the [CxOne CLI](https://checkmarx.com/resource/documents/en/34965-68621-checkmarx-one-cli-quick-start-guide.html).  The resulting container can be used to invoke scans from a CI/CD pipeline, the [CxFlow++ GitHub Action](https://github.com/checkmarx-ts/checkmarx-cxflow-plusplus-github-action), the [CxOne++ GitHub Action](https://github.com/checkmarx-ts/cxone-plusplus-github-action) or via [CxFlow++](#cxflow++).  

This is useful for organizations wishing to invoke supply chain scans
in a custom defined build environment.  The most common usage scenario
is to invoke a scan via a GitHub action on a self-hosted runner.  The
build environment container, running on-premise due to the self-hosted runner,
can be configured to access internal artifact hosting services.



## CxFlow++

This is a repackaged [CxFlow](https://github.com/checkmarx-ltd/cx-flow) container
published in the Checkmarx technical services' [package repository](https://github.com/orgs/checkmarx-ts/packages/container/package/cx-supply-chain-toolkit%2Fenhanced-cxflow-scaresolver).  
It adds the capability to set affinity
of code repository supply chain vulnerability scans with a build environment
properly defined for accurately generating a dependency tree.  This is
typically used by organizations that are invoking CxFlow scan orchestration
via web hooks.

