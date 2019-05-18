#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__create_date__ = '2019/4/10'
__all__ = ["Logger", "Logger_Easy", "Logger_Easy_Time", "Logger_Jack", "Null"]
"""
----Logger主要实现逻辑：
    1.输入对象(sys, self)：将logging信息封装为一个Msg实例。
    2.主体：负责管理和分发。
    3.输出对象(sys, self[.read()], file, email)：将Msg实例按预先设定的格式输出到相应的位置（屏幕/文件/发送邮件/自身储存）。

----示例用法请参见_tests(或者_examples)文件夹。
"""

import os
import sys
import traceback
from datetime import datetime
from typing import Union, List, Dict, ClassVar

IP_Level_dic = {'all': 6, 'debug': 1, 'info': 2, 'warning': 3, 'error': 4, 'critical': 5, "none": 0}
OP_Level_dic = {'all': 0, 'debug': 1, 'info': 2, 'warning': 3, 'error': 4, 'critical': 5, "none": 6}
FMT = {"none": "%(message)s",
       'simple': "[%(levelname)s] %(message)s",
       'info': "[%(levelname)s][%(time)s] %(message)s",
       'all': "[%(levelname)s][%(time)s][%(filename)s %(funcName)s()][%(processid)s/%(lineno)d][%(loggername)s] %(message)s",
       'debug': "[%(levelname)s][%(time)s][%(filename)s %(funcName)s()][%(processid)s/%(lineno)d] %(message)s",
       'multiprocess': "[%(levelname)s][%(time)s][PID:%(processid)s] %(message)s"}


# ----------------------------- Logger ------------------------------------
def _translate_op_level(OP_level) -> int:
    if isinstance(OP_level, str):
        return OP_Level_dic[OP_level.lower()]
    else:
        return OP_level + 0


class Msg:
    def __init__(self, IP_level_name: str, title, message, end):
        dt = datetime.now()
        self.levelname = IP_level_name.upper()
        self.pathname = sys.argv[0]
        self.filename = sys._getframe(2).f_code.co_filename
        self.funcName = sys._getframe(2).f_code.co_name
        self.processid = os.getpid()
        self.lineno = sys._getframe(2).f_lineno
        self.date = dt.strftime('%Y-%m-%d')
        self.datetime = dt.strftime('%Y%m%d%H%M%S')
        self.time = dt.strftime('%H:%M:%S')
        self.message = message
        self.IP_level = IP_Level_dic[IP_level_name]
        self.title = title
        self.end = end

    def __str__(self) -> str:
        return str(self.message) + str(self.end)

    def translate(self, fmt: str) -> str:
        if self.title is None:
            return fmt % self.__dict__ + "%s" % self.end
        else:
            return "%s%s%s" % (self.title, self.message, self.end)


class IP_Self:
    def write(self, msg: Msg) -> None:
        pass

    def flush(self) -> None:
        pass

    def debug(self, message, title=None, end="\n"):
        self.write(Msg("debug", title, message, end))

    def info(self, message, title=None, end="\n"):
        self.write(Msg("info", title, message, end))

    def warning(self, message, title=None, end="\n"):
        self.write(Msg("warning", title, message, end))

    def error(self, message, title=None, end="\n"):
        self.write(Msg("error", title, message, end))

    def critical(self, message, title=None, end="\n"):
        self.write(Msg("critical", title, message, end))


class IP_Sys:
    def __init__(self, logger, target: str, IP_level_name: str):
        self.logger = logger
        self.IP_level_name = IP_level_name
        if target not in ["stdout", "stderr"]:
            raise Exception("Wrong target {%s}. Pls give 'stdout' or 'stderr'. ")
        self.target = target
        self.keeper = getattr(sys, target)
        setattr(sys, target, self)

    def __del__(self):
        if self.keeper is not None:
            setattr(sys, self.target, self.keeper)
            self.keeper = None

    def myclear(self):
        self.__del__()

    def direct_write(self, txt: str):
        self.keeper.write(txt)

    def direct_flush(self):
        self.keeper.flush()

    def write(self, txt: str):
        """ take the place of builtins.print """
        if txt != "\n":
            self.logger.write(Msg(self.IP_level_name, "", txt, "\n"))

    def flush(self):
        self.logger.flush()


class _OP_base:
    def __init__(self, OP_level: Union[str, int] = "all", fmt: str = FMT['simple']):
        self.OP_level = _translate_op_level(OP_level)
        self.fmt = fmt

    def myclear(self):
        pass

    def write(self, msg: Msg):
        pass

    def flush(self):
        pass


class OP_Self(_OP_base):
    def __init__(self, OP_level: Union[str, int] = "all", fmt: str = FMT['simple']):
        _OP_base.__init__(self, OP_level, fmt)
        self.store = []

    def myclear(self):
        self.store = []

    def write(self, msg: Msg):
        if msg.IP_level >= self.OP_level:
            self.store.append(msg.translate(self.fmt))

    def read(self) -> str:
        return "".join(self.store)


class OP_File(OP_Self):
    def __init__(self, file_path: str, OP_level: Union[str, int] = "all", fmt: str = FMT['info']):
        OP_Self.__init__(self, OP_level, fmt)
        self.file_path = file_path

    def myclear(self):
        """这里不能让程序崩溃了，使用try。一次性写入有助于提高性能。"""
        try:
            with open(self.file_path, "a") as f:
                f.write(self.read())
        except Exception as e:
            OP_Sys.write_stderr(str(e))


class OP_Email(OP_Self):
    def __init__(self, account: str, password: str, server_addr: str, name: str,
                 subject: str, to_account: Union[str, List[str]], only_when_error=False,
                 OP_level: Union[str, int] = "all", fmt: str = FMT['info'], *args, **kwargs):
        OP_Self.__init__(self, OP_level, fmt)
        self.login = [account, password, server_addr, 465, name]
        self.subject = subject
        self.to_account = to_account
        self.only_when_error = only_when_error

    def myclear(self):
        """这里不能让程序崩溃了，使用try。"""
        if (not self.only_when_error) or (sys.exc_info()[0] is not None):
            if sys.exc_info()[0] is None:
                status = "Status: Success! Logger is clearing without Exception.\n" + "-" * 100 + "\n"
            else:
                status = "Status: Failed!!\n" + ''.join(traceback.format_exception(*sys.exc_info())) + "-" * 100 + "\n"
            try:
                from lewintools.pro.email import Outbox
                outbox = Outbox()
                outbox.login_ssl(*self.login)
                msg = outbox.write_MIMEtext_text(self.subject, status + self.read(), self.to_account)
                outbox.send_MIMEtext(self.to_account, msg)
            except Exception as e:
                msge = "Logger failed when sending eamil : %s. \n" % str(e)
                OP_Sys.write_stderr(msge)


class OP_Mongodb(OP_Self):
    def __init__(self, login: str, db: str, cl: str, subject: str, only_when_error=False,
                 OP_level: Union[str, int] = "all", fmt: str = FMT['info'], *args, **kwargs):
        """Login command: "mongodb://user:pwd@host:port/"  """
        OP_Self.__init__(self, OP_level, fmt)
        self.login = login
        self.db = db
        self.cl = cl
        self.subject = subject
        self.only_when_error = only_when_error
        self.stttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def myclear(self):
        """这里不能让程序崩溃了，使用try。一次性写入。"""
        if (not self.only_when_error) or (sys.exc_info()[0] is not None):
            val = {
                "Subject": self.subject,
                "SttTime": self.stttime,
                "EndTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            if sys.exc_info()[0] is None:
                val["Status"] = "ok"
                val["Log"] = self.read()
            else:
                val["Status"] = "err"
                status = "Status: Failed!!\n" + ''.join(traceback.format_exception(*sys.exc_info())) + "-" * 100 + "\n"
                val["Log"] = status + self.read()
            try:
                from pymongo import MongoClient
                with MongoClient(self.login) as mgdb:
                    mgcl = mgdb[self.db][self.cl]
                    mgcl.insert_one(val)
            except Exception as e:
                OP_Sys.write_stderr(str(e))


class OP_Sys(_OP_base):
    def write(self, msg: Msg):
        if msg.IP_level >= self.OP_level:
            if hasattr(sys.stdout, "direct_write"):
                getattr(sys.stdout, "direct_write")(msg.translate(self.fmt))
            else:
                getattr(sys.stdout, "write")(msg.translate(self.fmt))

    def flush(self):
        if hasattr(sys.stdout, "direct_flush"):
            getattr(sys.stdout, "direct_flush")()
        else:
            getattr(sys.stdout, "flush")()

    @staticmethod
    def write_stderr(txt):
        OP_Sys._direct(sys.stderr, "write", txt)

    @staticmethod
    def flush_stderr():
        OP_Sys._direct(sys.stderr, "flush")

    @staticmethod
    def write_stdout(txt):
        OP_Sys._direct(sys.stdout, "write", txt)

    @staticmethod
    def flush_stdout():
        OP_Sys._direct(sys.stdout, "flush")

    @staticmethod
    def _direct(target, method, *args):
        if hasattr(target, "direct_" + method):
            getattr(target, "direct_" + method)(*args)
        else:
            getattr(target, method)(*args)


class Logger(IP_Self):
    __date__ = "20190505"

    def __init__(self, name: str = None):
        if name is None:
            self._name = os.path.basename(sys._getframe(1).f_code.co_filename)
        else:  # must be str.
            self._name = name + ""
        # Outputers
        self.OPs = []
        self.IPs = []
        self.cleared = False

    def __del__(self):
        self.myclear()

    @property
    def name(self) -> str:
        return self._name

    # Safe mode (Context Manager) -------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.myclear()

    # Hub Station -----------------------------
    def write(self, msg: Msg) -> None:
        for OP in self.OPs:
            OP.write(msg)

    def flush(self) -> None:
        for OP in self.OPs:
            OP.flush()

    def myclear(self) -> None:
        if not self.cleared:
            for P in self.IPs + self.OPs:
                try:
                    P.myclear()
                except Exception as e:
                    print(e)
            self.cleared = True

    # Adding Outputers ------------------------------
    def _add_op(self, cls: ClassVar, *args, **kwargs):
        if not self.get_op_instances(cls):
            self.OPs.append(cls(*args, **kwargs))
        return self

    def add_op_sys(self, level="all", fmt: str = FMT['simple']):
        return self._add_op(OP_Sys, level, fmt)

    def add_op_self(self, level="all", fmt: str = FMT['simple']):
        return self._add_op(OP_Self, level, fmt)

    def add_op_file(self, file_path: str, level="all", fmt: str = FMT['simple']):
        return self._add_op(OP_File, file_path, level, fmt)

    def add_op_email(self, account: str, password: str, server_addr: str, name: str,
                     subject: str, to_account: Union[str, List[str]], only_when_error=False,
                     OP_level: Union[str, int] = "all", fmt: str = FMT['info'], *args, **kwargs):
        return self._add_op(OP_Email, account, password, server_addr, name, subject, to_account, only_when_error,
                            OP_level, fmt)

    def add_op_mongodb(self, login: str, db: str, cl: str, subject: str, only_when_error=False,
                       OP_level: Union[str, int] = "all", fmt: str = FMT['info'], *args, **kwargs):
        return self._add_op(OP_Mongodb, login, db, cl, subject, only_when_error, OP_level, fmt, *args, **kwargs)

    # Adding Inputers ------------------------------
    def add_ip_sys(self, target_level: Dict = None):
        if target_level is None:
            target_level = {"stdout": "info", "stderr": "error"}
        for target, level in target_level.items():
            if [IP for IP in self.IPs if (isinstance(IP, IP_Sys) and IP.target == target)]:
                continue
            else:
                self.IPs.append(IP_Sys(self, target, level))
        return self

    # manager -------------------------------
    def get_ip_instances(self, cls: ClassVar) -> list:
        return [IP for IP in self.IPs if isinstance(IP, cls)]

    def get_op_instances(self, cls: ClassVar) -> list:
        return [OP for OP in self.OPs if isinstance(OP, cls)]

    # special attribution -------------------------------
    def write_stderr(self, txt):
        OP_Sys.write_stderr(txt)

    def print_exception(self) -> None:
        except_info = ''.join(traceback.format_exception(*sys.exc_info()))
        sys.stderr.write(except_info)
        sys.stderr.flush()

    def print_hello(self) -> None:
        filename = "%s" % sys._getframe(1).f_code.co_filename
        self.write(Msg("all", "", filename.center(100, "-"), "\n"))

    def read(self) -> Union[str, List[str]]:
        ins = self.get_op_instances(OP_Self)
        if len(ins) == 1:
            return ins[0].read()
        elif len(ins) == 0:
            raise Exception("The logger have no OP_Self instance, so cant read().")
        else:
            return [i.read() for i in ins]


# ----------------------------- Other simple Logger ------------------------------------
class Logger_Easy:
    """很简单的logger，只调用了print，只是增加了levelname。"""
    __date__ = "2019.04.10"

    def debug(self, s):
        print("[debug]" + s)

    def info(self, s):
        print("[info]" + s)

    def warning(self, s):
        print("[warning]" + s)

    def error(self, s):
        print("[error]" + s)

    def critical(self, s):
        print("[critical]" + s)

    class easy_logging:
        debug = (lambda x: print("[debug]" + x))
        info = (lambda x: print("[info]" + x))
        warning = (lambda x: print("[warning]" + x))
        error = (lambda x: print("[error]" + x))
        critical = (lambda x: print("[critical]" + x))


class Logger_Easy_Time:
    """很简单的logger，只调用了print，只是增加了levelname和时间。"""
    __date__ = "2019.04.10"

    def debug(self, s):
        print("[%s][debug] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def info(self, s):
        print("[%s][info] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def warning(self, s):
        print("[%s][warning] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def error(self, s):
        print("[%s][error] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def critical(self, s):
        print("[%s][critical] %s" % (datetime.now().strftime("%H:%M:%S"), s))


class Logger_Jack:
    """
    Kidnap sys.stdout&sys.stderr, so is able to intercept prints. Then you can do anything on those loggings.
    ----捕获sys.std，可以截取所有企图通过print输出的信息，并保存在自身实例中，需要时可以读取。

    example用法：
    with Easy_Jack() as logger:
        # do something ...
        return logger.text
    """
    __date__ = "2019.04.10"

    def __init__(self):
        self.s = ""

    def __enter__(self):
        self.orig_stdout = sys.stdout
        sys.stdout = self
        self.orig_stderr = sys.stderr
        sys.stderr = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr
        return isinstance(exc_val, TypeError)

    def write(self, s):
        self.s += "%s" % s

    def flush(self):
        pass

    @property
    def text(self):
        return self.s


class Null:
    """安全地无视一切调用的终极哑巴对象。用于其他模块中作为默认logger（即默认不输出任何信息）。"""
    __date__ = "20190502"

    def __getattr__(self, item):
        def mute(*args, **kwargs):
            pass

        return mute

    def __call__(self, *args, **kwargs):
        pass
