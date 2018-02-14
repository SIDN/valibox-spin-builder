#!/usr/bin/env python

#
# Helper module based on the old create_release script.
# Called by the CreateRelease step
#

#
# This module packages up the changelog, version and built images
# and creates a json file containing the sha256sums so devices
# can check whether they need to update.
#
# In the (near) future, we should sign releases as well. This will
# be the place to do so.
#

import argparse
import datetime
import os
import shutil
import sys

class ReleaseEnvironmentError(Exception):
    pass

class ReleaseCreator:
    def __init__(self, targets, target_info_base_dir, version, changelog_filename, target_dir):
        self.targets = targets
        self.target_info_base_dir = target_info_base_dir
        self.images = []
        self.version = version
        self.changelog_filename = changelog_filename
        self.target_dir = target_dir
        self.sums = {}

    def check_environment(self):
        if not os.path.exists(self.changelog_filename):
            raise ReleaseEnvironmentError("Changelog file does not exist: %s" % self.changelog_filename)

        for target in self.targets:
            info_file = os.path.join(self.target_info_base_dir, "devices", target, "image_info")
            if not os.path.exists(info_file):
                raise ReleaseEnvironmentError("Image information file does not exist: %s" % info_file)

            with open(info_file) as inf:
                line = inf.readline()
                parts = line.split(",")
                if len(parts) != 2:
                    raise ReleaseEnvironmentError("Image information file (%s) does not contain <name>,<path>" % info_file)
                image_name = parts[0].strip()
                image_file = parts[1].strip()
                self.images.append((image_name, image_file))

    def create_target_tree(self):
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)
        for image in self.images:
            td = self.target_dir + os.sep + image[0]
            if not os.path.exists(td):
                os.mkdir(td)

    def copy_files(self):
        for image in self.images:
            shutil.copyfile("bin/targets/%s" % image[1], "%s/%s/sidn_valibox_%s_%s.bin" % (self.target_dir, image[0], image[0], self.version))
            shutil.copyfile(self.changelog_filename, "%s/%s/%s.info.txt" % (self.target_dir, image[0], self.version))

    def read_sha256sums(self):
        with open("bin/targets/ar71xx/generic/sha256sums", "r") as sumsfile:
            for line in sumsfile.readlines():
                for image in self.images:
                    imname = image[1].rpartition('/')[2]
                    if imname in line:
                        parts = line.split(" ")
                        print(parts)
                        self.sums[image[0]] = parts[0] + "\n"
        with open("bin/targets/ramips/mt7620/sha256sums", "r") as sumsfile:
            for line in sumsfile.readlines():
                for image in self.images:
                    imname = image[1].rpartition('/')[2]
                    if imname in line:
                        parts = line.split(" ")
                        self.sums[image[0]] = parts[0] + "\n"

    def create_versions_file(self):
        with open("%s/versions.txt" % self.target_dir, "w") as outputfile:
            for image in self.images:
                outputfile.write("%s %s %s/sidn_valibox_%s_%s.bin %s/%s.info.txt %s" %
                    (image[0], self.version, image[0], image[0], self.version, image[0], self.version, self.sums[image[0]]))

    def create_release(self):
        self.check_environment()
        self.read_sha256sums()
        self.create_target_tree()
        self.copy_files()
        self.create_versions_file()
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create ValiBox release file structure")
    parser.add_argument("-v", "--version", help="Version of the release (e.g. 1.0.2)")
    parser.add_argument("-b", "--beta", help="Create a beta release version (version number will be beta-<datetime>)", action="store_true")
    parser.add_argument("changelog", help="changelog file to put in the release")
    parser.add_argument("targetdir", help="target directory to place files in")

    args = parser.parse_args()

    if args.version is None and not args.beta:
        print("Need either a version (-v) or beta (-b)")
        sys.exit(1)
    if args.version is not None and args.beta:
        print("Can't specify both a version number and beta")
        sys.exit(1)

    if args.version is not None:
        version_number = args.version
    else:
        dt = datetime.datetime.now()
        version_number = "beta-%s" % dt.strftime("%Y%m%d%H%M")

    #print(version_number)
    rc = ReleaseCreator(version_number, args.changelog, args.targetdir)
    rc.create_release()
