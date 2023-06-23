# Checkmarx Supply Chain Toolkit

This repository contains tools for assisting deployment of supply chain vulnerability scanning with Checkmarx products. A complete user manual and downloadable components can be found in the [releases](releases) area to the left side of this page.

# Toolkit Contents Summary


## Build Environment Extension

The `build-extension` toolkit is a `Dockerfile` with associated artifacts that will extend an existing containerized build environment by adding
[SCA Resolver](https://checkmarx.com/resource/documents/en/34965-19196-checkmarx-sca-resolver.html).  The resulting container can be used to invoke SCA Resolver from a CI/CD pipeline or via [CxFlow++](#cxflow++)


## CxFlow++

This is a repackaged [CxFlow](https://github.com/checkmarx-ltd/cx-flow) container
published in the Checkmarx technical services' [package repository](https://github.com/orgs/checkmarx-ts/packages).  I adds the capability to set affinity
of code repository supply chain vulnerability scans with a build environment
properly defined for accurately generating a dependency tree.

1
