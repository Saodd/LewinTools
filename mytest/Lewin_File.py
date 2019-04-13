#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/13'
"""

"""

import os
import time
import random
import unittest
from datetime import datetime, timedelta
from LewinTools import Lewin_Findfiles, Easy_Logging_Time

# ————————————————————————————————————————————————————————
TEST_DIR = "C:/Users/lewin/mycode/data/test/Lewin_File"
# ————————————————————————————————————————————————————————
logger = Easy_Logging_Time()
ARG_now = datetime.now().replace(microsecond=0)
ARG_now2 = ARG_now - timedelta(hours=1)
ARG_today = ARG_now.replace(hour=0, minute=0, second=0)
ARGS = {ARG_now: "%Y%m%d_%H%M%S",
        ARG_now2: "%Y%m%d_%H%M%S",
        ARG_today: "%Y%m%d", }
ARG_days_before = -2
ARG_days_after = 1


# ————————————————————————————————————————————————————————
class Test__Lewin_Findfiles(unittest.TestCase):
    __date__ = "2019.04.13"

    def test_Date(self):
        versions = (Lewin_Findfiles.__date__, Test__Lewin_Findfiles.__date__)
        msg = "Lewin_Findfiles is [%s], but Test is [%s]" % (versions)
        self.assertEqual(*versions, msg=msg)

    def setUp(self) -> None:
        self.wsp = Lewin_Findfiles(path=TEST_DIR, logger=logger)

    # ——————————————————— find_lastone() —————————————————————
    def test__find_lastone__Lastday(self):
        arg_dt = ARG_today
        arg_fmt = ARGS[arg_dt]
        result = self.wsp.find_lastone(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile")
        want = "Test_{}.testfile".format((arg_dt + timedelta(ARG_days_after)).strftime(arg_fmt))
        self.assertEqual(want, result)

    def test__find_lastone__Lastday_Abspath(self):
        arg_dt = ARG_today
        arg_fmt = ARGS[arg_dt]
        result = self.wsp.find_lastone(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile", abspath=True)
        want = "Test_{}.testfile".format((arg_dt + timedelta(ARG_days_after)).strftime(arg_fmt))
        want = os.path.join(TEST_DIR, want)
        # mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        # self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))
        self.assertEqual(want, result)

    def test__find_lastone__Today(self):
        arg_dt = ARG_today
        arg_fmt = ARGS[arg_dt]
        result = self.wsp.find_lastone(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile", before=arg_dt)
        want = "Test_{}.testfile".format((arg_dt).strftime(arg_fmt))
        self.assertEqual(want, result)

    def test__find_lastone__Lastone(self):
        arg_dt = ARG_now
        arg_fmt = ARGS[arg_dt]
        result = self.wsp.find_lastone(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile")
        want = "Test_{}.testfile".format((arg_dt + timedelta(ARG_days_after)).strftime(arg_fmt))
        self.assertEqual(want, result)

    def test__find_lastone__Todaylastone(self):
        arg_dt = ARG_now
        arg_fmt = ARGS[arg_dt]
        result = self.wsp.find_lastone(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile", before=arg_dt)
        want = "Test_{}.testfile".format((arg_dt).strftime(arg_fmt))
        self.assertEqual(want, result)

    def test__find_lastone__Todayoldone(self):
        arg_dt = ARG_now2
        arg_fmt = ARGS[arg_dt]
        result = self.wsp.find_lastone(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile", before=arg_dt)
        want = "Test_{}.testfile".format((arg_dt).strftime(arg_fmt))
        self.assertEqual(want, result)

    # ——————————————————— easy_path() —————————————————————
    def test__easy_path__None(self):
        want = os.path.dirname(os.path.abspath(__file__))
        result = Lewin_Findfiles.easy_path()
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__here(self):
        want = os.path.dirname(os.path.abspath(__file__))
        result = Lewin_Findfiles.easy_path(".")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__parent(self):
        want = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = Lewin_Findfiles.easy_path("..")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__uncle(self):
        want = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uncle")
        result = Lewin_Findfiles.easy_path("../uncle")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__brother(self):
        want = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brother")
        result = Lewin_Findfiles.easy_path("./brother")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__son(self):
        want = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brother/son")
        result = Lewin_Findfiles.easy_path("./brother/son")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__out(self):
        want = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brother/son")
        result = Lewin_Findfiles.easy_path("./brother/son")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__Other_py(self):
        py = """
        """


class Environment:
    def __init__(self):
        self.files = []
        self.dir = TEST_DIR
        if not self.dir:
            exit("Please assign a dir where Test-program will create and delete some files.")
        elif not os.path.exists(self.dir):
            exit("The dir [%s] does not exits." % self.dir)

    def __enter__(self):
        dir = self.dir
        print(" Preparing environment ".center(100, '-'))
        for arg_dt, arg_fmt in ARGS.items():
            for days in range(ARG_days_before, ARG_days_after + 1):
                name_file = "Test_{}.testfile".format((arg_dt + timedelta(days)).strftime(arg_fmt))
                path_file = os.path.join(dir, name_file)
                if os.path.exists(path_file):
                    print("%s already exist!" % path_file)
                else:
                    try:
                        obj_file = open(path_file, 'w')
                    except Exception as e:
                        print("Failed when creating [%s]: %s" % (path_file, e))
                    else:
                        print("Created: %s" % path_file)
                        obj_file.close()
                        self.files.append(path_file)
        print(" Finished preparing environment ".center(100, '-'))
        time.sleep(0.5)  # Special for Pycharm. Coz stderr seems bad in Pycharm-windows.

    def __exit__(self, exc_type, exc_val, exc_tb):
        time.sleep(0.5)  # Special for Pycharm. Coz stderr seems bad in Pycharm-windows.
        print(" Recovering environment ".center(100, '-'))
        while len(self.files):
            path_file = self.files.pop()
            try:
                os.remove(path_file)
            except Exception as e:
                print("Failed when deleting [%s]: %s" % (path_file, e))
            else:
                print("Deleted: %s" % path_file)
        print(" Finished recovering environment ".center(100, '-'))
        return isinstance(exc_val, TypeError)


# ————————————————————————————————————————————————————————
# class Lewin_Findfiles:
#     def __init__(self, logger: LT.Lewin_Logging, path_test: str):
#         self.logger = logger
#         self.path_test = path_test
#
#     def test_find_lastone(self):
#         wksp = LT.Lewin_Findfiles(self.path_test, logger=logger, touch=True)
#         fmt_file = "test_%s.file"
#         prefix = "test_"
#         postfix = "\.file"
#         fmt_time = "%Y%m%d_%H%M%S"
#         # 准备测试环境
#         today = datetime.now()
#         today = datetime(today.year, today.month, today.day, today.hour)
#         today_earlier = datetime(today.year, today.month, today.day, today.hour - 1)
#         for i in [-3, -2, -1, 0, 1, 2]:
#             wksp.join_touch(fmt_file % (today + timedelta(i)).strftime(fmt_time))
#             wksp.join_touch(fmt_file % (today_earlier + timedelta(i)).strftime(fmt_time))
#         # 测试archive
#         wksp.archive(prefix=prefix, fmt=fmt_time, postfix=postfix, before=today + timedelta(-3), move_to=None)
#         wksp.archive(prefix=prefix, fmt=fmt_time, postfix=postfix, before=today + timedelta(-2), move_to="./arch")
#         # 打印当前供测试的文件
#         for file in wksp.find_all(prefix=prefix, fmt=fmt_time, postfix=postfix):
#             self.logger.debug(file, titile="")
#         n = 0
#         # -------------------------------------
#         description = "最最新的文件！"
#         n += 1
#         description = " {} ".format(str(n).center(100, "-"), description)
#         result = wksp.find_lastone(prefix=prefix, fmt=fmt_time, postfix=postfix)
#         want = fmt_file % (today + timedelta(2)).strftime(fmt_time)
#         mark = "Success" if os.path.commonpath([result]) == os.path.commonpath([want]) else "Fail"
#         print("{}\n想要:{}\n得到:{}\n判断:{}".format(description, want, result, mark))
#         # -------------------------------------
#         description = "当天的文件！"
#         n += 1
#         description = " {} ".format(str(n).center(100, "-"), description)
#         before = datetime(today.year, today.month, today.day + 1, hour=0)
#         result = wksp.find_lastone(prefix=prefix, fmt=fmt_time, postfix=postfix, before=before)
#         want = fmt_file % (today).strftime(fmt_time)
#         mark = "Success" if os.path.commonpath([result]) == os.path.commonpath([want]) else "Fail"
#         print("{}\n想要:{}\n得到:{}\n判断:{}".format(description, want, result, mark))
#
#
# # ————————————————————————————————————————————————————————
# if __name__ == '__main__':
#     logger = LT.Lewin_Logging().add_handler_stdout()
#
#     obj = Lewin_Findfiles(logger, "C:/Users/lewin/mycode/data/test/Lewin_File")
#     obj.test_find_lastone()

# ————————————————————————————————————————————————————————
if __name__ == '__main__':
    with Environment():
        unittest.main()
