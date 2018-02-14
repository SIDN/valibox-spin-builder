from .util import *
from .conditionals import *
from .steps import *

import collections
import configparser
import datetime


class BuildConfig:
    CONFIG_FILE = ".valibox_build_config"

    # format: section, name, default

    def __init__(self, config_file, defaults):
        if config_file is not None:
            self.config_file = config_file
        else:
            self.config_file = BuildConfig.CONFIG_FILE
        self.config = configparser.SafeConfigParser(dict_type=collections.OrderedDict)
        self.config.read_dict(defaults)
        self.config.read(self.config_file)

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def show_main_options(self):
        for option, value in self.config['main'].items():
            print("%s: %s" % (option, value))

    def get(self, section, option):
        return self.config.get(section, option)

    def getboolean(self, section, option):
        return self.config.getboolean(section, option)


class Builder:
    """
    This class creates and performs the actual steps in the configured
    build process
    """
    def __init__(self, steps):
        self.steps = steps
        self.read_last_step()

    def read_last_step(self):
        self.last_step = None
        if os.path.exists("./.last_step"):
            with open(".last_step") as inf:
                line = inf.readline()
                self.last_step = int(line)

    def get_last_step(self):
        return self.last_step

    # read or create the config
    def check_config():
        pass

    def print_steps(self):
        i = 1
        for s in self.steps:
            print("%s:\t%s" % (i, s))
            i += 1

    def save_last_step(self):
        with open(".last_step", "w") as out:
            out.write("%d\n" % self.last_step)

    def perform_steps(self):
        if self.last_step is not None and self.last_step > len(self.steps):
            print("Build already completed, use -r to restart from first step")
        failed_step = None
        if self.last_step is None:
            self.last_step = 1
        for step in self.steps[self.last_step - 1:]:
            self.save_last_step()
            print("step %d: %s" % (self.last_step, step))
            if not step.perform():
                print("step %d FAILED: %s" % (self.last_step, step))
                return self.last_step
            self.last_step += 1
        self.save_last_step()




class StepBuilder:
    """
    Steps builder helper class, with some convenience methods for repeated
    actions
    """
    def __init__(self):
        self.steps = []

    def add(self, step):
        """
        Add any type of Step
        """
        self.steps.append(step)
        return step

    def add_cmd(self, cmd, *args, **kwargs):
        """
        Add a CmdStep with the given command and arguments
        """
        step = CmdStep(cmd, *args, **kwargs)
        return self.add(step)
