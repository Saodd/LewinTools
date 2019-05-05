#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__create_date__ = '2019/4/10'
__all__ = ["Logger", "Logger_Easy", "Logger_Easy_Time", "Logger_Jack", "Null"]
"""

"""

import os, sys, traceback
from datetime import datetime
from typing import Union, List, Tuple, Dict, ClassVar

IP_Level_dic = {'all': 6, 'debug': 1, 'info': 2, 'warning': 3, 'error': 4, 'critical': 5, "none": 0}
OP_Level_dic = {'all': 0, 'debug': 1, 'info': 2, 'warning': 3, 'error': 4, 'critical': 5, "none": 6}
FMT = {"none": "%(message)s",
       'simple': "[%(levelname)s] %(message)s",
       'info': "[%(levelname)s][%(time)s] %(message)s",
       'all': "[%(levelname)s][%(time)s][%(filename)s %(funcName)s()][%(processid)s/%(lineno)d][%(loggername)s] %(message)s",
       'debug': "[%(levelname)s][%(time)s][%(filename)s %(funcName)s()][%(processid)s/%(lineno)d] %(message)s",
       'multiprocess': "[%(levelname)s][%(time)s][PID:%(processid)s] %(message)s"}


# ————————————————————————————————————————————————————————
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

    def direct_fulsh(self):
        self.keeper.flush()

    def write(self, txt: str):
        """ take the place of builtins.print """
        if txt != "\n":
            self.logger.write(Msg(self.IP_level_name, None, txt, "\n"))

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


class OP_Sys(_OP_base):
    def write(self, msg: Msg):
        if msg.IP_level >= self.OP_level:
            if hasattr(sys.stdout, "direct_write"):
                getattr(sys.stdout, "direct_write")(msg.translate(self.fmt))
            else:
                getattr(sys.stdout, "write")(msg.translate(self.fmt))

    def flush(self):
        if hasattr(sys.stdout, "direct_fulsh"):
            getattr(sys.stdout, "direct_fulsh")()
        else:
            getattr(sys.stdout, "flush")()


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
    def _add_op(self, cls: ClassVar, level: str, fmt: str):
        if not self.get_op_instances(cls):
            self.OPs.append(cls(level, fmt))
        return self

    def add_op_sys(self, level="all", fmt: str = FMT['simple']):
        return self._add_op(OP_Sys, level, fmt)

    def add_op_self(self, level="all", fmt: str = FMT['simple']):
        return self._add_op(OP_Self, level, fmt)

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
    def write_stderr(self, txt: str, end="\n", flush=False) -> None:
        txt += end
        if hasattr(sys.stderr, "direct_write"):
            getattr(sys.stderr, "direct_write")(txt)
        else:
            getattr(sys.stderr, "write")(txt)
        if flush:
            if hasattr(sys.stderr, "direct_flush"):
                getattr(sys.stderr, "direct_flush")(txt)
            else:
                getattr(sys.stderr, "flush")(txt)

    def print_exception(self) -> None:
        except_info = ''.join(traceback.format_exception(*sys.exc_info()))
        sys.stderr.write(except_info)
        sys.stderr.flush()

    def read(self) -> Union[str, List[str]]:
        ins = self.get_op_instances(OP_Self)
        if len(ins) == 1:
            return ins[0].read()
        elif len(ins) == 0:
            raise Exception("The logger have no OP_Self instance, so cant read().")
        else:
            return [i.read() for i in ins]


# ————————————————————————————————————————————————————————
class Logger_Easy:
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
    Kidnap sys.stdout&sys.stderr, so is able to intercept prints.
    with Easy_Jack() as logger:
        # do something ...
        loggings = logger.text
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
    __date__ = "20190502"

    def __getattr__(self, item):
        def mute(*args, **kwargs):
            pass

        return mute

    def __call__(self, *args, **kwargs):
        pass
