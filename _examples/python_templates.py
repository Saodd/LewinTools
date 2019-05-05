#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "${USER}"
__date__ = "${DATE}"
"""

"""

import os, sys


# ------------------------- Project Environment -------------------------
def _find_root(n):
    if n > 0: return os.path.dirname(_find_root(n - 1))
    return os.path.abspath(__file__)


_path_project = _find_root(2)
if _path_project not in sys.path: sys.path.insert(0, _path_project)

# ------------------------- Functions -------------------------


# ------------------------- Main -------------------------
if __name__ == "__main__":
    pass
