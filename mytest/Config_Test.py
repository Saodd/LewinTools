#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__all__ = ["test_config"]

import os


# ---------------------- class --------------------------------------
class _Testing_Config:
    def __init__(self):
        self.path_mytest = os.path.dirname(os.path.abspath(__file__))

    def join_make(self, path:str, dirname:str) -> str:
        path = os.path.join(path, dirname)
        if not os.path.isdir(path):
            os.mkdir(path)
            print("Made dir: %s " % path)
        return path

    @property
    def path__TestData(self) -> str:
        return self.join_make(self.path_mytest, "_TestData_")

    @property
    def path__Lewin_File(self) -> str:
        return self.join_make(self.path__TestData, "Lewin_File")

# ---------------------- instance --------------------------------------
test_config = _Testing_Config()
