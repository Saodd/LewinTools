#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__create_date__ = '2019/4/13'
"""

"""

import os
import sys
import time
import shutil
import unittest
from datetime import datetime, timedelta

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)
from lewintools import Findfiles, Logger_Easy_Time
from _tests._config import config_path

# —————————————————————————Assign testing directory———————————————————————————————
TEST_DIR = config_path.dir__base__file

# ————————————————————————Settings————————————————————————————————
logger = Logger_Easy_Time()
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
    __date__ = "20190422"

    def test__Version_Date(self):
        versions = (Findfiles.__date__, Test__Lewin_Findfiles.__date__)
        msg = "Findfiles is [%s], but Test is [%s]" % versions
        self.assertTrue(versions[0] < versions[1], msg=msg)

    def setUp(self) -> None:
        self.wsp = Findfiles(path=TEST_DIR)

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
        result = self.wsp.find_all(prefix="Test_", fmt="%Y", postfix="\\.testfile")
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
        result = Findfiles.easy_path()
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__here(self):
        want = os.path.dirname(os.path.abspath(__file__))
        result = Findfiles.easy_path(".")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__parent(self):
        want = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = Findfiles.easy_path("..")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__uncle(self):
        want = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uncle")
        result = Findfiles.easy_path("../uncle")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__brother(self):
        want = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brother")
        result = Findfiles.easy_path("./brother")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__son(self):
        want = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brother/son")
        result = Findfiles.easy_path("./brother/son")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__out(self):
        want = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brother/son")
        result = Findfiles.easy_path("./brother/son")
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    def test__easy_path__Other_py(self):
        sys.path.insert(0, TEST_DIR)
        mod_name = Environment.name_test_py.split(".py")[0]
        mod = __import__(mod_name)   # created when __enter__()
        want = TEST_DIR
        result = getattr(mod, "test_in_file")()
        mark = (os.path.commonpath([want]) == os.path.commonpath([result]))
        self.assertTrue(mark, msg="\nwant: {}\nresult: {}".format(want, result))

    # ——————————————————— archive() —————————————————————
    def test__archive__delete(self):
        arg_dt = ARG_now
        arg_fmt = ARGS[arg_dt]
        # create file
        files_before = self.wsp.find_all(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile")
        name_file = "Test_{}.testfile".format((arg_dt - timedelta(10)).strftime(arg_fmt))
        path_file = os.path.join(TEST_DIR, name_file)
        open(path_file, "w").close()
        assert os.path.exists(path_file)
        # archive file
        files_archived = self.wsp.archive(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile",
                                          before=(arg_dt - timedelta(9)), move_to=None)
        files_after = self.wsp.find_all(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile")
        # test
        self.assertEqual(files_archived, [(path_file, None)])
        self.assertEqual(files_before, files_after)

    def test__archive__move(self):
        arg_dt = ARG_now
        arg_fmt = ARGS[arg_dt]
        # create file
        files_before = self.wsp.find_all(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile")
        name_file = "Test_{}.testfile".format((arg_dt - timedelta(12)).strftime(arg_fmt))
        path_file = os.path.join(TEST_DIR, name_file)
        path_file_new = os.path.join(TEST_DIR, "archive", name_file)
        open(path_file, "w").close()
        assert os.path.exists(path_file)
        # archive file
        files_archived = self.wsp.archive(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile",
                                          before=(arg_dt - timedelta(11)), move_to="./archive")
        files_after = self.wsp.find_all(prefix="Test_", fmt=arg_fmt, postfix="\\.testfile")
        # test
        self.assertEqual(files_archived, [(path_file, path_file_new)])
        self.assertEqual(files_before, files_after)
        shutil.rmtree(os.path.join(TEST_DIR, "archive"))


# ————————————————————————————————————————————————————————
class Environment:
    script = """
from lewintools import Findfiles
def test_in_file():
    return Findfiles.easy_path(".")
                        """
    name_test_py = "file__easy_path__Other_py.py"
    path_test_py = os.path.join(TEST_DIR, name_test_py)

    def __init__(self, TEST_DIR: str):
        self.files = []
        self.dir = TEST_DIR
        if not self.dir:
            exit("Please assign a dir where Test-program will create and delete some files.")
        elif not os.path.exists(self.dir):
            exit("The dir [%s] does not exits." % self.dir)

    def __enter__(self):
        if len(os.listdir(self.dir)):
            exit("The testing directory [%s] is not empty!! Please clean it up." % self.dir)
        logger.info(" Preparing environment ".center(100, '-'))
        # prepare for date_files.
        for arg_dt, arg_fmt in ARGS.items():
            for days in range(ARG_days_before, ARG_days_after + 1):
                name_file = "Test_{}.testfile".format((arg_dt + timedelta(days)).strftime(arg_fmt))
                path_file = os.path.join(self.dir, name_file)
                if os.path.exists(path_file):
                    logger.warning("%s already exist!" % path_file)
                else:
                    try:
                        obj_file = open(path_file, 'w')
                    except Exception as e:
                        logger.error("Failed when creating [%s]: %s" % (path_file, e))
                    else:
                        logger.info("Created: %s" % path_file)
                        obj_file.close()
                        self.files.append(path_file)
        # prepare for python_file.
        try:
            with open(Environment.path_test_py, 'w') as f:
                f.write(Environment.script)
        except:
            logger.error("Failed when creating file: %s" % Environment.path_test_py)
        else:
            logger.info("Created file: %s" % Environment.path_test_py)
        logger.info(" Finished preparing environment ".center(100, '-'))
        time.sleep(0.5)  # Special for Pycharm. Coz stderr seems bad in Pycharm-windows.

    def __exit__(self, exc_type, exc_val, exc_tb):
        time.sleep(0.5)  # Special for Pycharm. Coz stderr seems bad in Pycharm-windows.
        logger.info(" Recovering environment ".center(100, '-'))
        # clean the whole directory.
        try:
            shutil.rmtree(TEST_DIR)
        except:
            logger.error("Failed when removing tree: %s" % TEST_DIR)
        else:
            logger.info("Removed tree: %s" % TEST_DIR)
        logger.info(" Finished recovering environment ".center(100, '-'))
        return isinstance(exc_val, TypeError)


if __name__ == '__main__':
    with Environment(TEST_DIR):
        unittest.main()
