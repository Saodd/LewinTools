#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/23'
"""

"""

import os, sys, unittest, time, _io
import traceback

# ———————————————————————环境变量—————————————————————————————————
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)
from lewintools.base.logging import Logger, IP_Sys


# ————————————————————————— Functions ———————————————————————————————
class Breaker:
    def __init__(self, txt=""):
        self.txt = txt

    def __enter__(self):
        time.sleep(0.1)
        if self.txt:
            print(self.txt.center(100, "↓"))
        else:
            print("↓" * 100)
        time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        time.sleep(0.1)
        if exc_type:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        time.sleep(0.1)
        print("\n" + "-" * 100 + "\n\n")
        time.sleep(0.1)
        return True


class Counter_stdout:
    def __init__(self):
        self.num = 0
        self.keep = None

    def __enter__(self):
        def jack(func):
            def counter(*args, **kwargs):
                self.num += 1  # 注意，print()会调用两次sys.std.write，第二次是一个换行符。
                # func(*args, **kwargs)

            return counter

        self.keep = sys.stdout.write
        sys.stdout.write = jack(sys.stdout.write)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.write = self.keep


def wrapper(myclass):
    def _wrapper(func):
        def inner(obj, *args, **kwargs):
            with myclass() as counter:
                num = func(obj, *args, **kwargs)
                obj.assertEqual(counter.num, num)

        return inner

    return _wrapper


# ————————————————————————— TestCase ———————————————————————————————
class Test__Lewin_Logging(unittest.TestCase):
    __date__ = "20190503"

    def test__Version_Date(self):
        versions = (Logger.__date__, Test__Lewin_Logging.__date__)
        msg = "Findfiles is [%s], but Test is [%s]" % versions
        self.assertTrue(versions[0] <= versions[1], msg)

    @wrapper(Counter_stdout)
    def test__op_sys(self):
        """ Default sys_OP_level=all. """
        with Logger().add_op_sys() as logger:
            logger.debug("+1")
            logger.info("+1")
            logger.warning("+1")
            logger.error("+1")
            logger.critical("+1")
        return 5

    @wrapper(Counter_stdout)
    def test__op_sys__warning(self):
        """ Default sys_OP_level=all. """
        with Logger().add_op_sys(level="warning") as logger:
            logger.debug("+0")
            logger.info("+0")
            logger.warning("+1")
            logger.error("+1")
            logger.critical("+1")
        return 3

    @wrapper(Counter_stdout)
    def test__ip_sys(self):
        with Logger().add_ip_sys() as logger:
            logger.debug("+0")
            logger.info("+0")
            logger.warning("+0")
            logger.error("+0")
            logger.critical("+0")
            print("++0")
        return 0

    @wrapper(Counter_stdout)
    def test__ip_op_sys(self):
        with Logger().add_ip_sys().add_op_sys() as logger:
            logger.debug("+1")
            logger.info("+1")
            logger.warning("+1")
            logger.error("+1")
            logger.critical("+1")
            print("+1")
        return 6

    @wrapper(Counter_stdout)
    def test__op_ip_sys(self):
        with Logger().add_op_sys().add_ip_sys() as logger:
            logger.debug("+1")
            logger.info("+1")
            logger.warning("+1")
            logger.error("+1")
            logger.critical("+1")
            print("+1")
        return 6

    @wrapper(Counter_stdout)
    def test__check_type__and__create_twice(self):
        """ Check type, and create twice. """
        with Logger().add_ip_sys().add_op_sys() as logger:
            self.assertIsInstance(sys.stdout, IP_Sys)
            self.assertIsInstance(sys.stderr, IP_Sys)
            logger.debug("+1")
            logger.info("+1")
            logger.warning("+1")
            logger.error("+1")
            logger.critical("+1")
            print("+1")
            sys.stderr.write("++++1")
        self.assertTrue(isinstance(sys.stdout, _io.TextIOWrapper))
        self.assertTrue(isinstance(sys.stderr, _io.TextIOWrapper))
        with Logger().add_op_sys().add_ip_sys({"stdout": "info"}) as logger:
            self.assertIsInstance(sys.stdout, IP_Sys)
            self.assertIsInstance(sys.stderr, _io.TextIOWrapper)
            logger.info("++1")
            print("+++1")
        self.assertIsInstance(sys.stdout, _io.TextIOWrapper)
        self.assertIsInstance(sys.stderr, _io.TextIOWrapper)
        return 9


class Test__Lewin_Logging__hand:
    def main(self):
        tests = [attr for attr in self.__dir__() if attr.startswith("test__")]
        with Breaker():
            for t in tests:
                getattr(self, t)(t)

    def test__stderr(self, func_name):
        with Breaker(" {%s}: see 3* RED. " % func_name):
            with Logger().add_ip_sys() as logger:
                sys.stderr.direct_write("something wrong.\n")
                logger.write_stderr("another wrong.")  # 捕获了sys.stderr的情况下能正常输出
            with Logger() as logger:
                logger.write_stderr("another wrong.")  # 没有捕获sys.stderr的情况下也能正常输出


# ————————————————————————— Main ———————————————————————————————
if __name__ == "__main__":
    Test__Lewin_Logging__hand().main()

    unittest.main()
