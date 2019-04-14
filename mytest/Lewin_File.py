#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__create_date__ = '2019/4/13'
"""

"""

import os
import sys
import time
import unittest
from datetime import datetime, timedelta

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from LewinTools import Lewin_Findfiles, Easy_Logging_Time

# —————————————————————————Assign testing directory———————————————————————————————
TRY_DIRS = ["E:/lewin/data/test/Lewin_File",
            "/home/lewin/data/test/Lewin_File",
            "C:/Users/lewin/mycode/data/test/Lewin_File"]
TEST_DIR = ""
for path in TRY_DIRS:
    if os.path.exists(path):
        TEST_DIR = path

# ————————————————————————Settings————————————————————————————————
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
    __date__ = "2019.04.14"

    def test_Date(self):
        versions = (Lewin_Findfiles.__date__, Test__Lewin_Findfiles.__date__)
        msg = "Lewin_Findfiles is [%s], but Test is [%s]" % versions
        self.assertEqual(*versions, msg=msg)

    def setUp(self) -> None:
        self.wsp = Lewin_Findfiles(path=TEST_DIR, logger=logger)

    # ——————————————————— find_all() —————————————————————
    def test__find_all__All(self):
        arg_dt = ARG_today
        arg_fmt = ARGS[arg_dt]
        want = set()
        for days in range(ARG_days_before, ARG_days_after + 1):
            name_file = "Test_{}.testfile".format((arg_dt + timedelta(days)).strftime(arg_fmt))
            want.add(name_file)
        result = self.wsp.find_all(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile")
        result = set(result)
        self.assertEqual(want, result)

    def test__find_all__None(self):
        result = self.wsp.find_all(prefix="Test_", fmt="%Y", postfix="\\.testfile", warning=False)
        self.assertEqual([], result)

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
        want = "Test_{}.testfile".format(arg_dt.strftime(arg_fmt))
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
        want = "Test_{}.testfile".format(arg_dt.strftime(arg_fmt))
        self.assertEqual(want, result)

    def test__find_lastone__Todayoldone(self):
        arg_dt = ARG_now2
        arg_fmt = ARGS[arg_dt]
        result = self.wsp.find_lastone(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile", before=arg_dt)
        want = "Test_{}.testfile".format(arg_dt.strftime(arg_fmt))
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
        pass

# ————————————————————————————————————————————————————————
class Environment:
    def __init__(self):
        self.files = []
        self.dir = TEST_DIR
        if not self.dir:
            exit("Please assign a dir where Test-program will create and delete some files.")
        elif not os.path.exists(self.dir):
            exit("The dir [%s] does not exits." % self.dir)

    def __enter__(self):
        if len(os.listdir(self.dir)):
            exit("The testing directory [%s] is not empty!! Please clean it up." % self.dir)
        print(" Preparing environment ".center(100, '-'))
        for arg_dt, arg_fmt in ARGS.items():
            for days in range(ARG_days_before, ARG_days_after + 1):
                name_file = "Test_{}.testfile".format((arg_dt + timedelta(days)).strftime(arg_fmt))
                path_file = os.path.join(self.dir, name_file)
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



if __name__ == '__main__':
    with Environment():
        unittest.main()
