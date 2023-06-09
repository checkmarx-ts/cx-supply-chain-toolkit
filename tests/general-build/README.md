# General Build Image

This repository contains a `Dockerfile` that can serve as a base build image for several languages.  While this is mostly
for testing purposes, it is possible to use this to compile one or more base build toolset images.  The resulting
base image can then be used as the base image for an SCA Resolver sandbox build image.

This base image is unsupported for any production build purposes.

# Installed Toolsets

* openjdk-11-jdk
* maven
* gradle
* ant
* yarn
* npm
* python3.11
* pip

# Building

`docker build -t <your tag> .`

