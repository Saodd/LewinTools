#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__all__ = ["config_path"]

import os


# ---------------------- class --------------------------------------
class Get_Path:
    def __init__(self):
        self.path_project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def join_make(self, path:str, dirname:str) -> str:
        path = os.path.join(path, dirname)
        if not os.path.isdir(path):
            os.mkdir(path)
            print("Made dir: %s " % path)
        return path

    @property
    def dir__Data(self) -> str:
        return self.join_make(self.path_project, "Data")

    @property
    def dir__base__file(self) -> str:
        return self.join_make(self.dir__Data, "file")

# ---------------------- instance --------------------------------------
config_path = Get_Path()
