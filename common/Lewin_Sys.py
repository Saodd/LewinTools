#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys
from .Lewin_Logging import Lewin_Logging, Easy_Logging

# ————————————————————————————————————————————————————————
class Append_Sys_Path:
    def __init__(self, path, logger:Lewin_Logging=None):
        if isinstance(logger, Lewin_Logging):
            self.logger = logger
        else:
            self.logger = Easy_Logging()
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