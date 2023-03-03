# Resolver-Sandbox: SCAResolver Execution Environment Management Solution

Executing SCAResolver has a few security considerations that are [discussed in the sandbox README](sandbox).  The sandboxed image
has two purposes:

* Isolate the execution of dependency resolution from access to sensitive data.
* Prevent the need to maintain custom builds of container images for dependency resolving.

The sandbox image build can be used to create images that invoke SCAResolver in a pipeline by utilizing container images that
are used in build pipelines for building the project.  Since these images are used in a build pipeline, they must contain a complete set of tools to build the project.
Since dependencies are resolved as part of the build, all the package management tools already exist in the build container image.  All that
is needed is to add SCAResolver and change the execution pattern to avoid vulnerability attack vectors related to dependency resolution.


# Current State

The sandbox image is considered in an Alpha release state.  Preliminary tests show it works as a method of invoking SCAResolver
in the appropriate tooling and security isolation context created from an existing container image.  Integration help can be obtained through Checkmarx Professional Services.


# Coming Next

## CxFlow and CxOne Invocation in Build Pipelines

Both CxFlow (invoked as a CLI) and the CxOne CLI 
currently invoke SCAResolver by passing a path to SCAResolver in the execution configuration.  This executes SCAResolver in
the correct build environment (as it is running in the build pipeline's container image), but does not provide the sandboxing to prevent
access to sensitive data available to the pipeline during dependency resolution.

An ability to invoke the sandboxed SCAResolver will be developed so that the dependency resolution is performed in both the correct build context
and the security isolation context.

## CxFlow with Webhooks

CxFlow invocation via webhook currently invokes SCAResolver in the context of the CxFlow container itself.  This means the CxFlow container must contain
every possible variant of build tool to be able to perform dependency resolution.  This has a few problems:

* The CxFlow container must be rebuilt with a comprehensive set of build tools installed and properly configured.
* Many AppSec teams find it challenging to understand which build tools are required to globally handle all dependency resolution needs.
* It may be infeasible to place all build tools into a single container.  Some tools may clash for a variety of reasons.

When invoking SCAResolver, the build environment must be compatible with the project.  There is currently no method of aligning the
build environment to the repository that generated the webhook event.

A method of tagging projects to align them with the correct SCAResolver sandbox image will be created.
