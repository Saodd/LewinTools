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
    def __init__(self, path="", touch=False, logger=None):
        path = Lewin_Findfiles.easy_path(path, call_back=1) # 读取的是调用位置的所在文件夹
        path = path.strip().rstrip('\\')
        if os.path.isdir(path):
            self.path = path
        elif touch:
            os.makedirs(path)
            print("[INFO] Created path: %s"%path)
            self.path = path
        else:
            raise Exception("[%s] is not a path. \nMaybe you can use Lewin_Findfiles(path, touch=True)."%path)
        if logger:
            self.logger = logger
        else:
            self.logger = Easy_Logging()
    def __str__(self):
        return self.path
    def path(self):
        return self.path

    def all_lastday(self, prefix="^", fmt='%Y%m%d', postfix="$", today:datetime=None, abspath=False, return_time=False):
        if today==None or today=="":
            today = datetime.now()
        elif type(today)==str and len(today)==8:
            today = datetime.strptime(today, "%Y%m%d")
        elif type(today)== datetime:
            pass
        else:
            raise Exception("wrong input format of arg [today]")
        file_list = os.listdir(self.path)
        filter_list = []
        re_com = re.compile(prefix + "(?P<time>.*?)" + postfix)
        for file in file_list:
            result = re.search(re_com, file)
            if result:
                time = result.groupdict()['time']
                try:
                    timestamp = datetime.strptime(time, fmt)
                except:
                    continue
                if timestamp > today:
                    continue
                if abspath:
                    filter_list.append([timestamp, os.path.join(self.path, file)])
                else:
                    filter_list.append([timestamp, file])

        if not len(filter_list):
            self.logger.warning("cannot find file named like: %s   in  %s."
                                %(prefix + "(?P<time>.*?)" + postfix, self.path))
        filter_list.sort(reverse=True)
        self.filter_list = filter_list
        if return_time:
            return filter_list
        else:
            return [file for timestamp, file in filter_list]
    def find_lastday(self, prefix="^", fmt='%Y%m%d', postfix="$", today:datetime=None, abspath=False, return_time=False):
        """search  prefix+20190127+postfix
            :return:  file = "prefix+20190127+postfix"         """
        result = self.all_lastday(prefix, fmt, postfix, today, abspath, return_time)
        if len(result):
            return result[0]
        else:
            return None
    def iter_lastday(self, prefix="^", fmt='%Y%m%d', postfix="$", today=None, abspath=False):
        self.all_lastday(prefix, fmt, postfix, today, abspath)
        while len(self.filter_list):
            timestamp, file = self.filter_list.pop(0)
            yield file
    def next_lastday(self):
        if len(self.filter_list):
            timestamp, file = self.filter_list.pop(0)
            return file
    def find_allday(self, prefix="", fmt='%Y%m%d', postfix=""):
        """search  prefix+20190127+postfix
            :return:  file = "prefix+20190127+postfix"         """
        file_list = os.listdir(self.path)
        find_list = []
        if prefix and (not prefix.startswith("^")):
            prefix = "^" + prefix
        if postfix and (not postfix.endswith("$")):
            postfix = postfix + "$"
        re_com = re.compile(prefix + "(.+?)" + postfix)
        for file in file_list:
            re_res = re_com.match(file)
            if re_res:
                try:
                    datetime.strptime(re_res.group(1), fmt)
                    find_list.append(file)
                except:
                    pass
        return find_list

    def all_last_mtime(self, pattern="^.+?$", now=None, abspath=False):
        if now == None or now == "":
            now = datetime.now().ctime()
        elif type(now) == datetime:
            now = now.ctime()
        else:
            raise Exception("wrong input format of arg [today]")
        file_list = os.listdir(self.path)
        ctime_list = []
        re_com = re.compile(pattern)
        for file in file_list:
            if re.search(re_com, file):
                print(os.path.join(self.path, file))
                timestamp = os.path.getmtime(os.path.join(self.path, file))
                # timestamp = datetime.strptime(timestamp, "%a %b %d %H:%M:%S %Y")
                print(timestamp, now)
                # TODO
                if timestamp > now:
                    continue
                if abspath:
                    ctime_list.append([timestamp, os.path.join(self.path, file)])
                else:
                    ctime_list.append([timestamp, file])

        if not len(ctime_list):
            self.logger.warning("cannot find file named like: %s" % (pattern))
        ctime_list.sort(reverse=True)
        self.ctime_list = ctime_list
        return [file for timestamp, file in ctime_list]

    def archive(self, prefix="^", fmt='%Y%m%d', postfix="$", before=None, delete=False,
                path="", dirname="./archive"):
        import shutil
        path = Lewin_Findfiles.easy_path(path, default_dir=self.path, dirname=dirname)
        archived = []
        for file in self.iter_lastday(prefix, fmt, postfix, today=before, abspath=True):
            if delete==True:
                os.remove(file)
                archived.append([file, "**deleted**"])
                self.logger.info("delete %s"%(file,))
            else:
                newfile = os.path.join(path, os.path.basename(file))
                if not os.path.isdir(os.path.dirname(newfile)):
                    os.makedirs(os.path.dirname(newfile))
                    self.logger.info("makedirs %s"%os.path.dirname(newfile))
                shutil.move(file, newfile)
                archived.append([file, newfile])
                self.logger.info("move %s to %s"%(file, newfile))
        return archived

    def join_touch(self, filename):
        path_file = os.path.join(self.path, filename)
        if not (filename in os.listdir(self.path)):
            open(path_file, 'w').close()
            self.logger.info("Created file: %s"%path_file)
        return path_file
    def join(self, filename):
        return os.path.join(self.path, filename)
    def join_exist(self, filename):
        path_file = os.path.join(self.path, filename)
        if not (filename in os.listdir(self.path)):
            raise Exception("File doesn't EXIST: %s"%path_file)
        return path_file
    def isfile(self, filename:str):
        path_file = self.join(filename=filename)
        return os.path.isfile(path_file)

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
            path = os.path.join(default_dir, path.lstrip('.')[1:])
            return path
        if not default_dir: default_dir = os.path.dirname(sys._getframe(1+call_back).f_code.co_filename)
        if path:
            if os.path.isabs(path):
                if "." in os.path.basename(path): # 如果是绝对路径，且以file名结尾
                    path = path
                else:  # 如果是绝对路径，且以dir名结尾
                    path = os.path.join(path, default_file)
            elif path.startswith("."):
                # 如果是相对路径"../something.txt"，先替换前面的"."
                path = replace_dot(path, default_dir)
                if "." in os.path.basename(path): # 相对路径处理后，且以file名结尾
                    path = path
                else:  # 相对路径处理后，且以dir名结尾
                    path = os.path.join(path, default_file)
            else:
                raise Exception("仅支持[绝对路径]或者[../]相对路径作为参数")
        else: #如果没有给path，先检查有没有给dirname或者filename
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
    def __init__(self, host, username, password, logger:Lewin_Logging=None):
        if logger==None:
            self.logger = Easy_Logging()
        elif isinstance(logger, Lewin_Logging):
            self.logger = logger
        else:
            raise Exception("wrong logger passed!! U give a %s! pls give None or Lewin_Logging."%type(logger))
        import ftplib
        self.ftp = ftplib.FTP(host)
        self.ftp.login(username, password)

    def __del__(self):
        try:
            self.ftp.quit()
        except:
            pass

    def download(self, path_remote:str, path_local:str):
        self.logger.info(path_local)
        with open(path_local, 'wb') as f:
            self.ftp.retrbinary("RETR %s" % path_remote, f.write)