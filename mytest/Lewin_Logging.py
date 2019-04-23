#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/23'
"""

"""

import os, sys, unittest, time, _io
import traceback
from multiprocessing import Process
from threading import Thread

# ———————————————————————环境变量—————————————————————————————————
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if path not in sys.path:
    sys.path.insert(0, path)
from LewinTools import Lewin_Logging


# ————————————————————————— Functions ———————————————————————————————
class breaker:
    def __enter__(self):
        time.sleep(0.1)
        print("↓" * 100)
        time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        time.sleep(0.1)
        if exc_type:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        time.sleep(0.1)
        print("↑" * 100 + "\n\n")
        time.sleep(0.1)
        return True


class Test__Lewin_Logging:
    __date__ = "2019.04.23"

    def test__Version_Date(self):
        versions = (Lewin_Logging.__date__, Test__Lewin_Logging.__date__)
        msg = "Lewin_Findfiles is [%s], but Test is [%s]" % versions
        if Lewin_Logging.__date__ != Test__Lewin_Logging.__date__:
            raise Exception(msg)

    def test__common_info(self):
        print(">>> you should see 5 lines:")
        with Lewin_Logging().add_op_sys() as logger:
            logger.debug("You should see this. The simplest logger.debug().")
            logger.info("You should see this.")
            logger.warning("You should see this.")
            logger.error("You should see this.")
            logger.critical("You should see this.")
            logger.myclear()

    def test__common_info_level(self):
        print(">>> you should see 3 lines:")
        with Lewin_Logging().add_op_sys(OP_level="warning") as logger:
            logger.debug("You should *not* see this.")
            logger.info("You should *not* see this.")
            logger.warning("You should see this.")
            logger.error("You should see this.")
            logger.critical("You should see this.")
            logger.myclear()

    def test__kidnap_sys(self):
        print(">>> you should see 8 lines:")
        with Lewin_Logging().add_op_sys().add_ip_sys() as logger:
            assert not isinstance(sys.stdout, _io.TextIOWrapper)
            assert not isinstance(sys.stderr, _io.TextIOWrapper)
            logger.debug("You should see this. Caught the sys.stdout, and give a debug.")
            logger.info("You should see this.")
            logger.warning("You should see this.")
            logger.error("You should see this.")
            logger.critical("You should see this.")
            print("You should see this. Simple print but you should see [INFO].")
        assert isinstance(sys.stdout, _io.TextIOWrapper)
        assert isinstance(sys.stderr, _io.TextIOWrapper)
        with Lewin_Logging().add_op_sys().add_ip_sys(IP_level_name="error") as logger2:
            # python是否有个懒惰机制？如果logger2与上个logger同名的话，就不会生成这个对象。print就消失了。
            assert not isinstance(sys.stdout, _io.TextIOWrapper)
            assert not isinstance(sys.stderr, _io.TextIOWrapper)
            logger2.info("You should see this.")
            print("You should see this. Simple print but you should see [ERROR].")

    def test__kidnap_sys_level(self):
        print(">>> you should see 3 lines:")
        with Lewin_Logging().add_op_sys(OP_level="warning").add_ip_sys() as logger:
            assert not isinstance(sys.stdout, _io.TextIOWrapper)
            assert not isinstance(sys.stderr, _io.TextIOWrapper)
            logger.info("You should *not* see this.")
            print("You should *not* see this.")
            logger.error("You should see this.")
        with Lewin_Logging().add_op_sys(OP_level="warning").add_ip_sys(IP_level_name="error") as logger3:
            assert not isinstance(sys.stdout, _io.TextIOWrapper)
            assert not isinstance(sys.stderr, _io.TextIOWrapper)
            logger3.info("You should *not* see this.")
            logger3.critical("You should see this.")
            print("You should see this.")


# ————————————————————————— Main ———————————————————————————————
if __name__ == "__main__":
    case = Test__Lewin_Logging()
    for attr in dir(case):
        if attr.startswith("test"):
            with breaker():
                getattr(case, attr)()
    print("All test finished!")
