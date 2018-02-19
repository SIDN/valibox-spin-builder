
This repository contains standard configurations for building the [Valibox](https://valibox.sidnlabs.nl) with [SPIN](https://spin.sidnlabs.nl) for specific architectures and devices, as well as a build tool that performs all the steps necessary to build complete images and packages for all the supported devices.

Main intended 'features':
* collect and store configurations without having a clone of lede-source
* build from scratch, but also from existing checkouts
* remember last build configuration
* resume build if failed or stopped, possibly with slightly altered settings (like -j1 V=s)
* options between 'build from repo' or 'build from local' (for example for spin)

# Build Tool

## Quick start

Check out this repository, create a separate build directory, and run the builder.

    git clone https://github.com/SIDN/valibox-spin-builder
    mkdir build
    cd build
    ../valibox-spin-builder/build.py -b

## Resuming/restarting

If the build is stopped (by manual break or because of a problem), you can resume the build with the same command:

    ../valibox-spin-builder/build.py -b

You can restart the build from the first step with -r:

    ../valibox-spin-builder/build.py -r

## Editing options

You can edit specific build options, such as target device, source repository branches, and verbose build by using

    ../valibox-spin-builder/build.py -e

After that, depending on the changes, you can either restart or resume the build.

## Showing all build steps without executing them

If you want to review all steps that will be performed for the current configuration, you can use

    ../valibox-spin-builder/build.py --print-steps


## Configuration options

There are several sections in the configuration:

* LEDE: Options for building the main LEDE image
* sidn_openwrt_pkgs: Options for the SIDN-specific packages
* SPIN: Options for SPIN
* Release: Options regarding the release you are building

Below is a full description of all options

Section | Option | Value type | Description
--------|--------|------------|------------
LEDE | update_git | True or False | Whether to do a git update before starting the build
LEDE | source_branch | &lt;string&gt; | The branch (or commit) of the lede-source tree to build
LEDE | target_device | &lt;name&gt; or "all" | Target device to build for, unless this is all it should be the name of one of the directories in the devices/ directory in this repository.
LEDE | update_all_feeds | True or False | Whether to always update all package feeds prior to building. If False, only the sidn feed is updated
LEDE | verbose_build | True or False | When true, LEDE is built with 'make -j1 V=s'
 | | |
sidn_openwrt_pkgs | update_git | True or False | Whether to do a git update before starting the build
sidn_openwrt_pkgs | source_branch | &lt;string&gt; | The source branch or commit of the SIDN package repository to check out
 | | |
SPIN | local | True or False | Use a local checkout of the SPIN code to build, instead of a published release version
SPIN | update_git | True or False | Whether to do a git update before starting the build
SPIN | source_branch | &lt;string&gt; | The source branch of commit of SPIN to build
 | | |
Release | create_release | True or False | Whether to create the release file structure after building. This creates a new directory structure valibox_release in your build directory, containing the images and meta-information that were built.
Release | version_string | &lt;version string&gt; | Version string to give to the release
Release | changelog_file | &lt;filename or empty&gt; | Changelog file to include in the release. If empty, the file Valibox_Changelog.txt from this repository will be used.
Release | target_directory | &lt;string&gt; | Directory to place the release directory structure in. Defaults to valibox_release
Release | beta | True or False | If True, the release version and filenames will have -beta-&lt;date&gt; added to them
Release | file_suffix | &lt;string or empty&gt; | An optional extra suffix for the release version and filenames


# Notes

* Building a custom local SPIN requires the SPIN source tree to have a version of create_tarball with the -n option; commits of SPIN older than 36dd2cd5 will likely fail.
* The builder does not recognize the situation where a build option is changed that influences a step that has already been performed; if changing options does not appear to have any effect, do a full rebuild with -r


# TODO

* Perhaps make the directories that are used for the repository checkouts configurable
* Add command-line flags for common configuration options

