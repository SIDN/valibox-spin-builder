import os
from .util import *

# Conditional:
# Only perform a step if the Conditional's perform() method
# returns True

# Some conditionals have a perform_if_false option, this reverses the
# result of perform()
class CmdOutputConditional:
    def __init__(self, cmd, expected, perform_if_false=False, directory=None):
        self.cmd = cmd
        self.expected = expected
        self.perform_if_false = perform_if_false
        self.directory = directory

    def perform(self):
        if self.directory is None:
            output = basic_cmd_output(self.cmd)
        else:
            with gotodir(self.directory):
                output = basic_cmd_output(self.cmd)
        if self.perform_if_false:
            return output != self.expected
        else:
            return output == self.expected

    def __str__(self):
        return "IF '%s' is %s'%s'" % (self.cmd, "not " if self.perform_if_false else "", self.expected)

class DirExistsConditional:
    def __init__(self, directory):
        self.directory = directory

    def perform(self):
        return os.path.exists(self.directory)

    def __str__(self):
        return "IF directory %s exists" % self.directory

class DirNotExistsConditional:
    def __init__(self, directory):
        self.directory = directory

    def perform(self):
        return not os.path.exists(self.directory)

    def __str__(self):
        return "IF directory %s does not exist" % self.directory
