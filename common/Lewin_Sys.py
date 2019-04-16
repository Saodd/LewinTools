#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
__version__ = "20190410"
"""

"""

import os, sys
from datetime import datetime


# ————————————————————————————————————————————————————————
class Append_Sys_Path:
    __date__ = "2019.04.14"

    def __init__(self, path, logger=None):
        if logger is None:
            self.logger = Easy_Logging_Time
        else:
            self.logger = logger
        if isinstance(path, list):
            self.path = list(set(path))
        else:
            self.path = [path]

    def __enter__(self):
        for pa in self.path:
            if os.path.isdir(pa):
                if pa not in sys.path:
                    sys.path.insert(0, pa)
                    self.logger.debug("append [%s] to sys path." % pa)
                else:
                    # 已经存在syspath了，就移除它，避免待会误删了影响其他程序。
                    self.path.remove(pa)
            else:
                self.logger.error("trying to add [%s] to python-path, but it is not a path." % self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for pa in self.path:
            sys.path.remove(pa)
            self.logger.debug("remove [%s] from sys path." % pa)
        return isinstance(exc_val, TypeError)

class Keep_Sys_Path:
    __date__ = "2019.04.16"

    def __init__(self, logger=None):
        if logger is None:
            self.logger = Easy_Logging_Time
        else:
            self.logger = logger


    def __enter__(self):
        self.path = [x for x in sys.path]

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            sys.path = [x for x in self.path]
        except Exception as e:
            self.logger.error("Failed when recovering sys.path !! %s"%e)
        else:
            self.logger.debug("Success recover sys.path.")
        return isinstance(exc_val, TypeError)
# ————————————————————————————————————————————————————————
class Easy_Logging_Time:
    __date__ = "2019.04.10"

    def debug(self, s):
        print("[%s][debug] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def info(self, s):
        print("[%s][info] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def warning(self, s):
        print("[%s][warning] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def error(self, s):
        print("[%s][error] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def critical(self, s):
        print("[%s][critical] %s" % (datetime.now().strftime("%H:%M:%S"), s))