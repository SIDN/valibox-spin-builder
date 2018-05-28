import os
import shlex
import subprocess

#
# General utility classes and functions
#
class gotodir:
    def __init__(self, directory):
        self.go_to_dir = directory
        self.orig_dir = None

    def __enter__(self):
        self.orig_dir = os.getcwd()
        os.chdir(self.go_to_dir)
        return self

    def __exit__(self, *args):
        if self.orig_dir is not None:
            os.chdir(self.orig_dir)

def basic_cmd(cmd, may_fail = False):
    print("Running: '%s'" % cmd)
    print("in dir: " + os.getcwd())
    rcode = subprocess.call(cmd, shell=True)
    print("Result: %d" % rcode)
    if may_fail:
        return True
    else:
        return rcode == 0

def basic_cmd_output(cmd):
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
    (stdout, _) = p.communicate()
    return stdout.decode("utf-8").strip()
