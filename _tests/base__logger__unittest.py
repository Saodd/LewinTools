#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
"""

"""

import os, sys, unittest, time, _io
import traceback
from datetime import datetime

# ———————————————————————环境变量—————————————————————————————————
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)
from lewintools.base.logging import Logger, IP_Sys
from _tests._config import Environment, config_path
from Lewin_Keys import Email_Account_monitor163 as Email_Account

TEST_DIR = config_path["dir__base__logging"]


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
__test_date__ = "20190505"


class Test__Lewin_Logging(unittest.TestCase):
    def test__Version_Date(self):
        versions = (Logger.__date__, __test_date__)
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

    def test__op_file(self):
        path_log = os.path.join(TEST_DIR, "log1.log")
        msg = "%s" % datetime.now()
        with Logger().add_op_file(path_log) as logger:
            logger.info(msg)
        with open(path_log, "r") as f:
            log = f.read()
        self.assertEqual(log, "[INFO] %s\n" % msg)


class Test__Lewin_Logging__hand:
    def main(self):
        tests = [attr for attr in self.__dir__() if attr.startswith("test__")]
        with Breaker():
            for t in tests:
                getattr(self, t)(t)

    def test__stderr(self, func_name):
        with Breaker(" {%s}: see 3* RED. " % func_name):
            with Logger().add_ip_sys() as logger:
                sys.stderr.direct_write("see1 red.\n")
                logger.write_stderr("see2 red.\n")  # 捕获了sys.stderr的情况下能正常输出
            with Logger() as logger:
                logger.write_stderr("see3 red.\n")  # 没有捕获sys.stderr的情况下也能正常输出

    def test__print_exception(self, func_name):
        with Breaker(" {%s}: see 2 group exception. " % func_name):
            with Logger().add_ip_sys().add_op_sys() as logger:  # 捕获了sys.stderr的情况下能正常输出
                try:
                    raise Exception("You should see this *stdout*. with add_ip_sys.")
                except:
                    logger.print_exception()
            time.sleep(0.1)
            with Logger() as logger:  # 没有捕获sys.stderr的情况下也能正常输出
                try:
                    raise Exception("You should see this *stderr*. without add_ip_sys.")
                except:
                    logger.print_exception()

    def test__read(self, func_name):
        with Breaker(" {%s}: see 1 group exception. " % func_name):
            with Logger().add_ip_sys().add_op_self() as logger:
                try:
                    logger.info("hello!")
                    raise Exception("You should see this *stdout*. with add_ip_sys.")
                except:
                    logger.print_exception()  # 没有add_op_sys，所以屏幕上看不见
                s = logger.read()
            print(s)  # 要显式的打印出来才能看见
            print(logger.read())  # 打印了一个空白行，因为执行了myclear()


class Test__Lewin_Logging__email:
    def main(self):
        tests = [attr for attr in self.__dir__() if attr.startswith("test__")]
        with Breaker():
            for t in tests:
                getattr(self, t)()

    @classmethod
    def test__email__all(cls):
        print("you should see +1 email.")
        with Logger() as logger:
            logger.add_op_email(account=Email_Account["account"], password=Email_Account["password"],
                                server_addr=Email_Account["server_addr"], name=Email_Account["name"],
                                subject="Testing logger", to_account=Email_Account["account"],
                                only_when_error=False)
            logger.info("Hello! Nothing wrong here.")

    @classmethod
    def test__email__only_when_error(cls):
        print("you should see +0 email.")
        with Logger() as logger:
            logger.add_op_email(account=Email_Account["account"], password=Email_Account["password"],
                                server_addr=Email_Account["server_addr"], name=Email_Account["name"],
                                subject="Testing logger", to_account=Email_Account["account"],
                                only_when_error=True)
            logger.info("you should not see thie email.")

    @classmethod
    def test__email__exception__only_false(cls):
        print("you should see +1 email.")
        try:
            with Logger() as logger:
                logger.add_op_email(account=Email_Account["account"], password=Email_Account["password"],
                                    server_addr=Email_Account["server_addr"], name=Email_Account["name"],
                                    subject="Testing logger", to_account=Email_Account["account"],
                                    only_when_error=True)
                raise Exception("Raise Exception! you should see this email!")
        except:
            pass



# ————————————————————————— Main ———————————————————————————————
if __name__ == "__main__":
    with Environment(TEST_DIR):
        Test__Lewin_Logging__hand().main()

        unittest.main()
    # Test__Lewin_Logging__email().main()
