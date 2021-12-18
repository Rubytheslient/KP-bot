import inspect
import os
def getremovepath(path):
    return os.path.splitext(os.path.basename(path))[0]
class printer():
    def __init__(self):
        self.level = 1
    def info(self, *msg):
        if self.level >= 1:
            print(f"[\033[1;32mInfo\033[1;37m][{getremovepath(inspect.stack()[1].filename)}]", *msg)
    def warn(self, *msg):
        if self.level >= 2:
            print(f"[\033[1;33mwarn\033[1;37m][{getremovepath(inspect.stack()[1].filename)}]", *msg)
    def error(self, *msg):
        if self.level >= 3:
            print(f"[\033[1;31merror\033[1;37m][{getremovepath(inspect.stack()[1].filename)}]", *msg)
    def debug(self, *msg):
        if self.level >= 4:
            print(f"[\033[1;36mdebug\033[1;37m][{getremovepath(inspect.stack()[1].filename)}]", *msg)
