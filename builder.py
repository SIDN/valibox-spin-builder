#!/usr/bin/python3

#
# build tool helper
#

# There are many moving parts, and while building one release
# for one specific architecture isn't that hard, we need to
# be able to build images based on different branches from different
# sources, etc.
#
# This toolkit was created to unify the multiple scripts we had to
# build the images
#

# Todo:
# - maybe split up into several minitools?
#   e.g. 'create-config, show-config, show-commands, run/continue'?
#   and/or curses based setup?
# start with command line tools

import argparse
import collections
import datetime
import os
import subprocess
import sys

from valibox_builder.util import *
from valibox_builder.conditionals import *
from valibox_builder.steps import *

from valibox_builder.builder import BuildConfig, Builder, StepBuilder

DEFAULT_CONFIG = collections.OrderedDict((
    ('main', collections.OrderedDict((
    ))),
    ('OpenWRT', collections.OrderedDict((
                ('update_git', True),
                ('source_branch', 'v18.06.1'),
                ('target_device', 'all'),
                ('update_all_feeds', False),
                ('make_arguments', ''),
    ))),
    ('sidn_openwrt_pkgs', collections.OrderedDict((
                ('update_git', True),
                ('source_branch', 'master'),
    ))),
    ('SPIN', collections.OrderedDict((
                ('local', True),
                ('update_git', True),
                ('source_branch', 'master'),
    ))),
    ('Release', collections.OrderedDict((
                ('create_release', True),
                ('version_string', '1.6'),
                ('changelog_file', ''),
                ('target_directory', 'valibox_release'),
                ('beta', True),
                ('file_suffix', "")
    ))),
))

def build_steps(config):
    sb = StepBuilder()

    #
    # OpenWRT sources
    #
    steps = []
    if config.getboolean("OpenWRT", "update_git"):
        sb.add_cmd("git clone https://github.com/openwrt/openwrt openwrt").if_dir_not_exists('openwrt')
        sb.add_cmd("git fetch").at("openwrt")
        sb.add(GitBranchStep(config.get("OpenWRT", "source_branch"), "openwrt"))
        # pull errors if the 'branch' is a detached head, so it may fail
        sb.add_cmd("git pull").at("openwrt").may_fail()

    #
    # SIDN Package feed sources
    #
    sidn_pkg_feed_dir = "sidn_openwrt_pkgs"
    if config.getboolean("sidn_openwrt_pkgs", "update_git"):
        sb.add_cmd("git clone https://github.com/SIDN/sidn_openwrt_pkgs %s" % sidn_pkg_feed_dir).if_dir_not_exists('sidn_openwrt_pkgs')
        sb.add_cmd("git fetch").at("sidn_openwrt_pkgs")
        sb.add(GitBranchStep(config.get("sidn_openwrt_pkgs", "source_branch"), "sidn_openwrt_pkgs"))
        sb.add_cmd("git pull").at("sidn_openwrt_pkgs").may_fail()

    #
    # SPIN Sources (if we build from local checkout)
    # If we build SPIN locally, we need to check it out as well (
    # (and perform magic with the sidn_openwrt_pkgs checkout)
    #
    if config.getboolean("SPIN", "local"):
        if config.getboolean("SPIN", "update_git"):
            sb.add_cmd("git clone https://github.com/SIDN/spin").if_dir_not_exists("spin")

            # only relevant if we use a local build of spin
            sb.add_cmd("git fetch").at("spin")
            sb.add(GitBranchStep(config.get("SPIN", "source_branch"), "spin"))
            sb.add_cmd("git pull").at("spin").may_fail()

        # Create a local release tarball from the checkout, and
        # update the PKGHASH and location in the package feed data
        # TODO: there are a few hardcoded values assumed here and in the next few steps
        sb.add_cmd("./scripts/create_tarball.sh -n").at("spin")
        sb.add_cmd("rm -f dl/spin-*.tar.gz").at("openwrt")
        sb.add_cmd("rm -f dl/lua-minittp-*.tar.xz").at("openwrt")

        # Set that in the pkg feed data; we do not want to change the repository, so we make a copy and update that
        orig_sidn_pkg_feed_dir = sidn_pkg_feed_dir
        sidn_pkg_feed_dir = sidn_pkg_feed_dir + "_local"
        sb.add_cmd("git checkout-index -a -f --prefix=../%s/" % sidn_pkg_feed_dir).at(orig_sidn_pkg_feed_dir)

        sb.add(UpdatePkgMakefile(sidn_pkg_feed_dir, "spin/Makefile", "/tmp/spin-0.7-beta.tar.gz"))

    #
    # Update general package feeds in OpenWRT
    #
    sb.add(UpdateFeedsConf("openwrt", sidn_pkg_feed_dir))
    if config.getboolean('OpenWRT', 'update_all_feeds'):
        # Always update all feeds
        sb.add_cmd("./scripts/feeds update -a").at("openwrt")
        sb.add_cmd("./scripts/feeds install -a").at("openwrt")
    else:
        # Only update sidn feed if the rest have been installed already
        sb.add_cmd("./scripts/feeds update sidn").at("openwrt").if_dir_exists("package/feeds/packages")
        sb.add_cmd("./scripts/feeds install -a -p sidn").at("openwrt").if_dir_exists("package/feeds/packages")

        # Update all feeds if they haven't been installed already
        sb.add_cmd("./scripts/feeds update -a").at("openwrt").if_dir_not_exists("package/feeds/packages")
        sb.add_cmd("./scripts/feeds install -a").at("openwrt").if_dir_not_exists("package/feeds/packages")


    #
    # Determine target devices
    #
    target_device = config.get('OpenWRT', 'target_device')
    if target_device == 'all':
        targets = [ 'gl-ar150', 'gl-mt300a', 'gl-6416', 'innotek-gmbh-virtualbox', 'raspberrypi,3-model-b' ]
    else:
        targets = [ target_device ]

    #
    # Prepare the version string of the release
    #
    version_string = config.get("Release", "version_string")
    if config.getboolean("Release", "beta"):
        dt = datetime.datetime.now()
        version_string += "-beta-%s" % dt.strftime("%Y%m%d%H%M")
    if config.get("Release", "file_suffix") != "":
        version_string += "_%s" % config.get("Release", "file_suffix")

    #
    # Build the OpenWRT image(s)
    #
    for target in targets:
        valibox_build_tools_dir = get_valibox_build_tools_dir()
        sb.add_cmd("rm -rf files").at("openwrt")
        sb.add_cmd("cp -r %s/devices/%s/files ./files" % (valibox_build_tools_dir, target)).at("openwrt")
        # Add the current changelog file and a version file
        sb.add_cmd("mkdir -p ./files/").at("openwrt")
        sb.add_cmd("cp -r %s ./files/valibox_changelog.txt" % (get_changelog_file(config))).at( "openwrt")
        sb.add(ValiboxVersionStep(version_string)).at("openwrt")
        sb.add_cmd("cp %s/devices/%s/diffconfig ./.config" % (valibox_build_tools_dir, target)).at("openwrt")
        sb.add_cmd("make defconfig").at("openwrt")
        # Some packages handle multi-arch building really badly, so we clean them all for each target
        sb.add_cmd("make package/clean").at("openwrt")
        build_cmd = "make"
        if config.get("OpenWRT", "make_arguments") != "":
            build_cmd += " %s" % config.get("OpenWRT", "make_arguments")
        sb.add_cmd(build_cmd).at("openwrt")

        # Some targets require a few extra steps
        # Note: there are more additional steps for a nice user experiece;
        # we should provide a vdi for virtualbox for instance; but those
        # steps are more related to updating the website, i think
        if target == 'innotek-gmbh-virtualbox':
            sb.add_cmd("gunzip -fk openwrt-x86-64-combined-squashfs.img.gz").at("openwrt/bin/targets/x86/64/")
        if target == 'raspberrypi,3-model-b':
            sb.add_cmd("gunzip -fk openwrt-brcm2708-bcm2710-rpi-3-ext4-factory.img.gz").at("openwrt/bin/targets/brcm2708/bcm2710/")

    #
    # And finally, move them into a release directory structure
    #
    if config.getboolean("Release", "create_release"):
        sb.add(CreateReleaseStep(targets, get_valibox_build_tools_dir(),
                    version_string, get_changelog_file(config),
                    config.get("Release", "target_directory")).at("openwrt"))

    return sb.steps


# Return the directory of this toolkit; needed to get device information
def get_valibox_build_tools_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_changelog_file(config):
    changelog_file = config.get("Release", "changelog_file")
    if changelog_file == "":
        changelog_file = get_valibox_build_tools_dir() + "/Valibox_Changelog.txt";
    return changelog_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', action="store_true", help='Start or continue the build from the latest step in the last run')
    parser.add_argument('-r', '--restart', action="store_true", help='(Re)start the build from the first step')
    parser.add_argument('-e', '--edit', action="store_true", help='Edit the build configuration options')
    parser.add_argument('-c', '--config', default=BuildConfig.CONFIG_FILE, help="Specify the build config file to use (defaults to %s)" % BuildConfig.CONFIG_FILE)
    #parser.add_argument('--check', action="store_true", help='Check the build configuration options')
    parser.add_argument('--print-steps', action="store_true", help='Print all the steps that would be performed')
    args = parser.parse_args()

    config = BuildConfig(args.config, DEFAULT_CONFIG)
    builder = Builder(build_steps(config))

    if args.build:
        builder.perform_steps()
    elif args.restart:
        builder.last_step = 1
        builder.perform_steps()
    elif args.edit:
        EDITOR = os.environ.get('EDITOR','vi')
        config.save_config()
        subprocess.call([EDITOR, config.config_file])
    elif args.print_steps:
        builder.print_steps()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
