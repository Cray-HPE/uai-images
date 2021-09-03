# UAI Images Repo

This repos provides container images and supporting installation tools for User Access Instances (UAI)s.  These images are used in conjunction with the User Access Service (UAS) Manager to provide isolated lightweight disposable login environmnents for users.

### A Note on Versions

The first version of this repository is 1.2.4.  This is because the content here was moved here from the following github repos:

- https://github.com/Cray-HPE/uai-util version 1.0.13
- https://github.com/Cray-HPE/switchboard version 1.2.3

starting the build products for this repo at version 1.2.4 avoids regressing the semantic versioning and colliding with pre-existing build products.

## Content Overview

The following HPE provided UAI images are built from the source in this repo:

- The Broker UAI Image
- The Basic Minimal SLES-15 UAI Image
- The UAS/UAI Self-Test UAI Image

In addition to this, the Update UAS kubernetes job's Helm chart and container image come from here.

### Broker UAI Image

A Broker UAI is a point of access that generates new personal UAIs in response to successful logins by users.  HPE provides a Broker UAI image that can be customized through the use of volume mounts for customer use.  This broker image contains the logic to authenticate users and spawn / find UAIs for users when they log in.

### Basic Minimal SLES-15 UAI Image

HPE ships a basic UAI Image that can be used to create UAIs mostly for sanity testing purposes.  This UAI Image provides a minimal login environment used to demostrate that UAS / UAI is working prior to the creation and deployment of custom UAI images by the site.

### UAS/UAI Self-Test UAI Image

The UAS/UAI self test mechanism uses a special UAI which contains the self-test logic for UAS/UAI.  When launched, this UAI image verifies operational correctness of UAS and then removes itself.

### Update UAS Job

The Update UAS Kubernetes job registers the UAI images generated here with UAS as needed, and makes other necessary adjustments to UAS configuration to adapt to image version changes.  The job runs when its helm chart is deployed or udgraded and ensures that the HPE supplied container images and related configuration are kept up to date.

## Development

Builds, unit testing and chart testing are run out of Makefiles driven by a top-level Makefile.  These can be run natively as long as you have the following installed on your native system:

- Make
- Docker
- Helm

These are available for most platforms, see installation instructions for your specific system.

Builds also run under Jenkins in the algo60 project.  All feature branches are built as unstable, while tags are built as stable.

### Native Builds

To build everything natively, simply use:

```
$ make
```

in the top level directory.  It is also possible to build individual components by running

```
$ make
```

in any of the sub-directories containing a `Makefile`.

### Unit Testing

To run unit tests on all components, simply use:

```
$ make unit_test
```

in the top level directory.  It is also possible to run unit tests on individual components by running

```
$ make unit_test
```

in any of the sub-directories containing a `Makefile`.


### Helm Chart Tests

To run Helm chart tests on all components, simply use:

```
$ make chart_test
```

in the top level directory.  It is also possible to run chart tests on individual components by running

```
$ make chart_test
```

in any of the sub-directories containing a `Makefile`.


## Release

To relase a stable version of this code merge your changes into `main` and add a tag of the form:

```
v1.2.4
```
