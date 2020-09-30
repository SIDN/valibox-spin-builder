from .conditionals import *
from .util import *
from .releasecreator import ReleaseCreator


class Step():
    def at(self, directory):
        self.directory = directory
        return self

    def if_true(self, conditional):
        self.conditional = conditional

    def if_not_cmd(self, cmd, result):
        self.conditional = CmdOutputConditional(cmd, result, True, self.directory)

    def if_dir_not_exists(self, directory):
        self.conditional = DirNotExistsConditional(directory)

    def if_dir_exists(self, directory):
        self.conditional = DirExistsConditional(directory)

    def may_fail(self):
        self._may_fail = True

class CmdStep(Step):
    def __init__(self, cmd, directory=None, may_fail=False, skip_if=None, conditional=None):
        self.directory = directory
        self.cmd = cmd
        self._may_fail = may_fail
        self.skip_if = skip_if
        self.conditional = conditional

    def __str__(self):
        if self.directory is not None:
            step_str = "in %s: %s" % (self.directory, self.cmd)
        else:
            step_str = "in current dir: %s" % (self.cmd)
        if self.conditional is not None:
            return "%s\n\t%s" % (self.conditional, step_str)
        else:
            return step_str

    def perform(self):
        if self.skip_if is not None and self.skip_if:
            return True

        if self.conditional is not None:
            if not self.conditional.perform():
                return True

        if self.directory is not None:
            print("[XX] directory set! " + self.directory)
            with gotodir(self.directory):
                return basic_cmd(self.cmd, may_fail=self._may_fail)
        else:
            return basic_cmd(self.cmd, may_fail=self._may_fail)

class GitBranchStep(CmdStep):
    def __init__(self, branch, directory):
        self.branch = branch
        CmdStep.__init__(self, "git checkout %s" % branch)
        self.at(directory)
        self.if_not_cmd('git rev-parse --abbrev-ref HEAD', branch)

class UpdateFeedsConf(Step):
    def __init__(self, directory, feed_dir):
        self.directory = directory
        self.line_to_add = "src-link sidn %s\n" % os.path.abspath(feed_dir)

    def __str__(self):
        return "in %s: add '%s' to feeds.conf" % (self.directory, self.line_to_add.strip())

    def perform(self):
        with gotodir(self.directory):
            with open("feeds.conf", "w") as out_file:
                with open("feeds.conf.default", "r") as in_file:
                    for line in in_file.readlines():
                        out_file.write(line)
                    out_file.write(self.line_to_add)
        return True

class UpdatePkgMakefile(Step):
    def __init__(self, directory, makefile, source_url, source_branch):
        self.directory = directory
        self.makefile = makefile
        self.source_url = source_url
        self.source_branch = source_branch

    def __str__(self):
        return "in %s: Update the OpenWRT package makefile %s to use %s as the git source" % (self.directory, self.makefile, self.source_url)

    def perform(self):
        with gotodir(self.directory):
            # First, get the hash of the tarfile
            #hash_line = basic_cmd_output("sha256sum %s" % self.tarfile)
            #if hash_line is None:
            #    # print error?
            #    return False
            #hash_str = hash_line.split(" ")[0]

            # Read the makefile, and update it in a tmp file
            # should we use mktempfile for this, or is this ok?
            with open(self.makefile, "r") as infile:
                with open(self.makefile + ".tmp", "w") as outfile:
                    for line in infile.readlines():
                        if line.startswith("PKG_SOURCE_URL:="):
                            outfile.write("PKG_SOURCE_URL:=%s\n" % self.source_url)
                        elif line.startswith("LATEST_COMMIT"):
                            outfile.write(line.replace("master", self.source_branch))
                        else:
                            outfile.write(line)
            # seems like we succeeded, overwrite the makefile
            return basic_cmd("cp %s %s" % (self.makefile + ".tmp", self.makefile))

class CreateReleaseStep(Step):
    def __init__(self, targets, target_info_base_dir, version_number, changelog_file, target_directory, directory=None):
        self.version_number = version_number
        self.changelog_file = changelog_file
        self.target_directory = target_directory
        self.directory = directory
        self.rc = ReleaseCreator(targets, target_info_base_dir, version_number, changelog_file, os.path.abspath(target_directory))

    def perform(self):
        try:
            if self.directory is not None:
                with gotodir(self.directory):
                    return self.rc.create_release()
            else:
                return self.rc.create_release()
        except Exception as exc:
            print("Release creation failed: " + str(exc))
            return False

    def __str__(self):
        return "In: %s: Create the file structure for release %s, and place them in %s" % (self.directory, self.version_number, self.target_directory)

class ValiboxVersionStep(Step):
    """
    This step creates the "/valibox.version" file
    """
    VERSIONFILE = "files/valibox.version"

    def __init__(self, version_string, directory=None):
        self.version_string = version_string
        self.directory = directory

    def perform(self):
        try:
            if self.directory is not None:
                with gotodir(self.directory):
                    return self.writefile()
            else:
                return self.writefile()
        except Exception as exc:
            print("Error writing valibox.version file: " + str(exc))
            return False

    def __str__(self):
        return "In: %s: Write the string '%s' to %s" % (self.directory, self.version_string, self.VERSIONFILE)

    def writefile(self):
        with open(self.VERSIONFILE, "w") as outf:
            outf.write("%s\n" % self.version_string)
        return True
