#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/11'
"""

"""

import os, sys, re, time
from datetime import datetime, timedelta
import LewinTools as LT


# ————————————————————————————————————————————————————————
class Lewin_Findfiles:
    def __init__(self, logger: LT.Lewin_Logging, path_test: str):
        self.logger = logger
        self.path_test = path_test

    def test_find_lastone(self):
        wksp = LT.Lewin_Findfiles(self.path_test, logger=logger, touch=True)
        fmt_file = "test_%s.file"
        prefix = "test_"
        postfix = "\.file"
        fmt_time = "%Y%m%d_%H%M%S"
        # 准备测试环境
        today = datetime.now()
        today = datetime(today.year, today.month, today.day, today.hour)
        today_earlier = datetime(today.year, today.month, today.day, today.hour-1)
        for i in [-3, -2, -1, 0, 1, 2]:
            wksp.join_touch(fmt_file % (today + timedelta(i)).strftime(fmt_time))
            wksp.join_touch(fmt_file % (today_earlier + timedelta(i)).strftime(fmt_time))
        # 测试archive
        wksp.archive(prefix=prefix, fmt=fmt_time, postfix=postfix, before=today + timedelta(-3), move_to=None)
        wksp.archive(prefix=prefix, fmt=fmt_time, postfix=postfix, before=today + timedelta(-2), move_to="./arch")
        # 打印当前供测试的文件
        for file in wksp.find_all(prefix=prefix, fmt=fmt_time, postfix=postfix):
            self.logger.debug(file, titile="")
        n = 0
        # -------------------------------------
        description = "最最新的文件！"
        n += 1
        description = " {} ".format(str(n).center(100, "-"), description)
        result = wksp.find_lastone(prefix=prefix, fmt=fmt_time, postfix=postfix)
        want = fmt_file % (today + timedelta(2)).strftime(fmt_time)
        mark = "Success" if os.path.commonpath([result]) == os.path.commonpath([want]) else "Fail"
        print("{}\n想要:{}\n得到:{}\n判断:{}".format(description, want, result, mark))
        # -------------------------------------
        description = "当天的文件！"
        n += 1
        description = " {} ".format(str(n).center(100, "-"), description)
        before = datetime(today.year, today.month, today.day+1, hour=0)
        result = wksp.find_lastone(prefix=prefix, fmt=fmt_time, postfix=postfix, before=before)
        want = fmt_file % (today).strftime(fmt_time)
        mark = "Success" if os.path.commonpath([result]) == os.path.commonpath([want]) else "Fail"
        print("{}\n想要:{}\n得到:{}\n判断:{}".format(description, want, result, mark))


# ————————————————————————————————————————————————————————
if __name__ == '__main__':
    logger = LT.Lewin_Logging().add_handler_stdout()

    obj = Lewin_Findfiles(logger, "C:/Users/lewin/mycode/data/test/Lewin_File")
    obj.test_find_lastone()
