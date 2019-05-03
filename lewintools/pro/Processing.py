#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/23'
__all__ = ["Lewin_Logging_Pro"]
"""

"""

import os, sys
from multiprocessing import Process, Queue, Pool, Manager
import threading

# ———————————————————————环境变量—————————————————————————————————
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if path not in sys.path:
    sys.path.insert(0, path)
from LewinTools.common.Lewin_Logging import Lewin_Logging


# ————————————————————————— Functions ———————————————————————————————
class Lewin_Logging_Pro(Lewin_Logging):
    pass

# ————————————————————————— Main ———————————————————————————————
