#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys, re
from datetime import datetime
from .Lewin_Logging import Easy_Logging, Lewin_Logging


# ————————————————————————————————————————————————————————
class Lewin_Findfiles:
    __date__ = "2019.04.12"

    def __init__(self, path: str = "", touch: bool = False, logger: Lewin_Logging = None):
        path = Lewin_Findfiles.easy_path(path, call_back=1)  # 读取的是调用位置的所在文件夹
        path = path.strip()
        if logger:
            self.logger = logger
        else:
            self.logger = Easy_Logging()
        if os.path.isdir(path):
            self._path = path
        elif touch:
            try:
                os.makedirs(path)
            except:
                raise
            else:
                self.logger.info("Created path: %s" % path)
                self._path = path
        else:
            raise Exception("[%s] is not a path. \nMaybe you can use Lewin_Findfiles(path, touch=True)." % path)
        self._result = []

    def __str__(self):
        return "%s" % self.path

    @property
    def path(self):
        return self._path

    @property
    def result(self):
        return self._result

    def find_all(self, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None, abspath=False,
                 return_time=False):
        # 支持一个特例，虽然这样不太健康。
        if isinstance(before, str) and len(before) == 8:
            before = datetime.strptime(before, "%Y%m%d")
        # 开始查找
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
                if return_time:
                    if abspath:
                        filter_list.append([timestamp, os.path.join(self._path, file)])
                    else:
                        filter_list.append([timestamp, file])
                else:
                    if abspath:
                        filter_list.append(os.path.join(self._path, file))
                    else:
                        filter_list.append(file)
        # 返回结果
        if len(filter_list):
            filter_list.sort(reverse=True)
        else:
            self.logger.warning("cannot find file: [%s] before [%s] in [%s]."
                                % (prefix + "(%s)" % fmt + postfix, before, self._path))
        self._result = filter_list
        return filter_list

    def find_lastone(self, prefix="^", fmt='%Y%m%d', postfix="$", before: datetime = None, abspath=False,
                     return_time=False):
        result = self.find_all(prefix, fmt, postfix, before, abspath, return_time)
        if result:
            return result[0]
        else:
            return None

    def archive(self, prefix="^", fmt='%Y%m%d', postfix="$", before=None, move_to="./archive"):
        """if (move_to=None) will delete target files; else will move to (move_to)."""
        import shutil
        archived = []
        if move_to:
            move_to = Lewin_Findfiles.easy_path(move_to, default_dir=self.path)
            for file in self.find_all(prefix, fmt, postfix, before=before, abspath=True):
                newfile = os.path.join(move_to, os.path.basename(file))
                if not os.path.isdir(os.path.dirname(newfile)):
                    os.makedirs(os.path.dirname(newfile))
                    self.logger.info("Make dirs %s" % os.path.dirname(newfile))
                try:
                    shutil.move(file, newfile)
                except Exception as e:
                    self.logger.error("Failed when moving {%s} to {%s}: {%s}" % (file, newfile, e))
                else:
                    archived.append([file, newfile])
                    self.logger.info("Move {%s} to {%s}." % (file, newfile))
        else:
            for file in self.find_all(prefix, fmt, postfix, before=before, abspath=True):
                try:
                    os.remove(file)
                except Exception as e:
                    self.logger.error("Failed when deleting {%s}: {%s}" % (file, e))
                else:
                    archived.append([file, None])
                    self.logger.info("Delete file {%s}." % (file,))
        return archived

    def join_touch(self, filename, raise_exception=True):
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

    def join(self, filename):
        return os.path.join(self.path, filename)

    def isfile(self, filename: str):
        path_file = self.join(filename=filename)
        return os.path.isfile(path_file)

    @staticmethod
    def easy_path(path="", dirname="", filename="", default_dir="", default_file="", call_back=0):
        '''
        :param path:
        :param dirname:
        :param filename:
        :param default_dir:     os.path.dirname(sys._getframe(1 +self.if_do).f_code.co_filename)
        :param default_file:    'log%s.log'%datetime.now().strftime("%Y%m%d")
        :return:
        '''

        # TODO: 这里默认了带'.'的都是文件（而不会是文件夹），会有隐含的bug。
        def replace_dot(path, default_dir):
            dot_num = len(path) - len(path.lstrip('.'))
            for i in range(dot_num - 1):
                default_dir = os.path.dirname(default_dir)
            path = os.path.join(default_dir, path.lstrip("./\\"))
            return path

        if not default_dir: default_dir = os.path.dirname(sys._getframe(1 + call_back).f_code.co_filename)
        if path:
            if os.path.isabs(path):
                if "." in os.path.basename(path):  # 如果是绝对路径，且以file名结尾
                    path = path
                else:  # 如果是绝对路径，且以dir名结尾
                    path = os.path.join(path, default_file)
            elif path.startswith("."):
                # 如果是相对路径"../something.txt"，先替换前面的"."
                path = replace_dot(path, default_dir)
                if "." in os.path.basename(path):  # 相对路径处理后，且以file名结尾
                    path = path
                else:  # 相对路径处理后，且以dir名结尾
                    path = os.path.join(path, default_file)
            else:
                raise Exception("仅支持[绝对路径]或者[../]相对路径作为参数")
        else:  # 如果没有给path，先检查有没有给dirname或者filename
            if dirname:
                if "." in os.path.basename(dirname):
                    raise Exception("dirname参数 不应该 带有'.'号。")
                elif dirname.startswith("."):
                    dirname = replace_dot(dirname, default_dir)
                else:
                    dirname = dirname
            else:
                dirname = default_dir
            if filename:
                if filename.startswith('\\') or filename.startswith('/'):
                    raise Exception("filename参数 不应该 以分隔符\\ /开头。")
                elif "." not in os.path.basename(filename):
                    raise Exception("filename参数 应该 带有'.'号。")
                else:
                    filename = filename
            else:
                filename = default_file
            path = os.path.join(dirname, filename)
        return path


# ————————————————————————————————————————————————————————
class Lewin_Ftp:
    __date__ = "2019.04.10"

    def __init__(self, host, username, password, logger: Lewin_Logging = None):
        if logger == None:
            self.logger = Easy_Logging()
        elif isinstance(logger, Lewin_Logging):
            self.logger = logger
        else:
            raise Exception("wrong logger passed!! U give a %s! pls give None or Lewin_Logging." % type(logger))
        import ftplib
        self.ftp = ftplib.FTP(host)
        self.ftp.login(username, password)

    def __del__(self):
        try:
            self.ftp.quit()
        except:
            pass

    def download(self, path_remote: str, path_local: str):
        self.logger.info(path_local)
        with open(path_local, 'wb') as f:
            self.ftp.retrbinary("RETR %s" % path_remote, f.write)


# ————————————————————————————————————————————————————————
class Others:
    def __init__(self):
        self.path = "something else."

    def pdf_to_txt(self, pdf_path, txt_path, fmt):
        pdf_path = Lewin_Findfiles.easy_path(filename=pdf_path, default_dir=self.path)
        txt_path = Lewin_Findfiles.easy_path(filename=txt_path, default_dir=self.path)

        import pandas as pd
        import pdfplumber
        # 参考 https://github.com/jsvine/pdfplumber#table-extraction-methods

        with pdfplumber.open(pdf_path) as pdf:
            tables = []
            for page in pdf.pages:
                for table in page.extract_tables(fmt):
                    tables += table
            df = pd.DataFrame(tables)
            df.to_csv(txt_path, index=False)

        return txt_path
