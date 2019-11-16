#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__all__ = ["Findfiles"]
"""

"""

import os, re, sys
from datetime import datetime
from typing import List, Tuple, Union
from lewintools import Null


# ------------------------------------------------
class Findfiles:
    __date__ = "2019.04.22"

    def __init__(self, path: str = "", touch: bool = False, logger=None) -> None:
        path = Findfiles.easy_path(path, call_back=1)  # 读取的是调用位置的所在文件夹
        path = path.strip()
        if logger:
            self.logger = logger
        else:
            self.logger = Null()
        if os.path.isdir(path):
            self._path = path
        elif touch:
            os.makedirs(path)
            self.logger.info("Created path: %s" % path)
            self._path = path
        else:
            raise Exception("[%s] is not a path. \nMaybe you can use Findfiles(path, touch=True)." % path)
        self._result = []

    def __str__(self) -> str:
        return "%s" % self.path

    @property
    def path(self) -> str:
        return self._path

    @property
    def result(self) -> list:
        return self._result

    def find_all_withdate(self, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None,
                          abspath: bool = False) -> List[Tuple[datetime, str]]:
        # 支持一个特例，虽然这样不太健康。
        if isinstance(before, str) and len(before) == 8:
            before = datetime.strptime(before, "%Y%m%d")
        # 开始查找 --------------------------------
        file_list = os.listdir(self._path)
        filter_list = []
        re_com = re.compile(prefix + "(?P<time>.*?)" + postfix)
        for file in file_list:
            result = re_com.findall(file)
            if result:
                time = result[0]
                try:
                    timestamp = datetime.strptime(time, fmt)
                except:
                    continue
                if before and timestamp > before:
                    continue
                if abspath:
                    filter_list.append((timestamp, os.path.join(self._path, file)))
                else:
                    filter_list.append((timestamp, file))
        # 返回结果 --------------------------------
        if len(filter_list):
            filter_list.sort(reverse=True)
        else:
            self.logger.warning("cannot find file: [%s] before [%s] in [%s]."
                                % (prefix + "(%s)" % fmt + postfix, before, self._path))
        self._result = filter_list
        return filter_list

    def find_all(self, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None, abspath: bool = False
                 ) -> List[str]:
        return [x[1] for x in self.find_all_withdate(prefix, fmt, postfix, before, abspath)]

    def find_lastone_withdate(self, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None, abspath=False,
                              ) -> Union[Tuple[datetime, str], Tuple[None, None]]:
        result = self.find_all_withdate(prefix, fmt, postfix, before, abspath)
        if result:
            return result[0]
        else:
            # coz we expect "date, filename = obj.find_lastone_withdate()" so return a *Tuple* instead of a *None*.
            return (None, None)

    def find_lastone(self, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None, abspath=False,
                     ) -> Union[str, None]:
        result = self.find_all_withdate(prefix, fmt, postfix, before, abspath)
        if result:
            return result[0][1]
        else:
            return None

    def join_touch(self, filename, raise_exception=True) -> str:
        if "." not in filename:
            raise Exception("Only support file-like name, it's dangerous to give a dir-like name: {%s}." % filename)
        path_file = self.join(filename=filename)
        if not os.path.exists(path_file):
            try:
                open(path_file, 'w').close()
            except Exception as e:
                self.logger.error("Failed when create file {%s}: %s" % (path_file, e))
                if raise_exception:
                    raise
            else:
                self.logger.info("Created file: %s" % path_file)
        return path_file

    def join(self, filename) -> str:
        return os.path.join(self.path, filename)

    def isfile(self, filename: str) -> bool:
        path_file = self.join(filename=filename)
        return os.path.isfile(path_file)

    @staticmethod
    def replace_dot(path, start_dir: str) -> str:
        """
        替换前面的dot，转换为绝对路径。
        """
        dot_num = len(path) - len(path.lstrip('.'))
        for i in range(dot_num - 1):
            start_dir = os.path.dirname(start_dir)
        path = os.path.join(start_dir, path.lstrip("./\\"))
        return path

    @staticmethod
    def easy_path(path="", start_dir: str = None, call_back: int = 0) -> str:
        """
        两个目标：
        1.找到调用位置程序所在的目录；
        2.替换前面的dot，转换为绝对路径。
        """
        if not start_dir:
            start_dir = os.path.dirname(os.path.abspath(sys._getframe(1 + call_back).f_code.co_filename))
        if path:
            if path.startswith("."):
                result = Findfiles.replace_dot(path, start_dir)
            elif os.path.isabs(path):
                result = path
            else:
                msg = "path=[{}], start_dir=[{}], call_back=[{}]".format(path, start_dir, call_back)
                raise Exception("I dont know what you want: %s" % msg)
        else:
            result = start_dir
        return result

    def archive(self, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None, move_to="./archive") \
            -> List[Tuple[str, Union[str, None]]]:
        """if (move_to=None) will delete target files; else will move to (move_to).
        :return:
            move: [(old_file_path, new_file_path), ...]
            delete: [(old_file_path, None), ...]
        """
        import shutil
        archived = []
        if move_to:
            move_to = Findfiles.easy_path(move_to, start_dir=self.path)
            try:
                os.makedirs(move_to)
            except FileExistsError:
                pass
            else:  # if create a dir, must show off.
                self.logger.info("Make dirs: %s" % move_to)
            for file in self.find_all(prefix, fmt, postfix, before=before, abspath=True):
                newfile = os.path.join(move_to, os.path.basename(file))
                try:
                    shutil.move(file, newfile)
                except Exception as e:
                    self.logger.error("Failed when moving {%s} to {%s}: {%s}" % (file, newfile, e))
                else:
                    archived.append((file, newfile))
                    self.logger.info("Move {%s} to {%s}." % (file, newfile))
        else:
            for file in self.find_all(prefix, fmt, postfix, before=before, abspath=True):
                try:
                    os.remove(file)
                except Exception as e:
                    self.logger.error("Failed when deleting {%s}: {%s}" % (file, e))
                else:
                    archived.append((file, None))
                    self.logger.info("Delete file {%s}." % (file,))
        return archived


# short cut -------------------------------------------------------
def find_all_withdate(dirpath: str, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None,
                      abspath: bool = False):
    file_list = os.listdir(dirpath)
    filter_list = []
    re_com = re.compile(prefix + "(?P<time>.*?)" + postfix)
    for file in file_list:
        result = re_com.findall(file)
        if result:
            time = result[0]
            try:
                timestamp = datetime.strptime(time, fmt)
            except:
                continue
            if before and timestamp > before:
                continue
            if abspath:
                filter_list.append((timestamp, os.path.join(dirpath, file)))
            else:
                filter_list.append((timestamp, file))
    if len(filter_list):
        filter_list.sort(reverse=True)
    else:
        print("cannot find file: [%s] before [%s] in [%s]." % (prefix + "(%s)" % fmt + postfix, before, dirpath))
    return filter_list
