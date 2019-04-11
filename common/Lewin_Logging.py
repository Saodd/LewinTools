#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys, time
from datetime import datetime


# ————————————————————————————————————————————————————————
class Lewin_Logging:
    """
    本模块结构：
    输入（logging / sys）---->  (Lewin_Logging模块) ---->  输出(handler_file, handler_stdout, ...)

    ——————————————————————用法——————————————————————————————————————
    1.把sys.stdout和stderr截取一份并复制
        [用法] logger = Lewin_Logging().catch_sys()
    2.将所有屏幕输出都导出到文件中（带一个True就会复制屏幕输出）
        [用法] logger.add_handler_file(path='all_log.txt', level='all')
    3.把全部日志打印到屏幕上（要显式指定）；把error以上的日志保存到另一个文件中
        [用法] logger.add_handler_stdout(level='all')
        [用法] logger.add_handler_file(path='error_log.txt', level='error')
        [用法] logger.add_handler_file(path='error_log.txt', level='error', fmt="%(message)s")
    4.生成日志
        [用法] logger.info("test log info!")
        [用法] logger.error("test log error!")
    5.傻瓜操作
        from lewin_tools import Lewin_Logging
        logger = Lewin_Logging().catch_sys().add_handler_file().add_handler_stdout()
        logger.do(function)

    ——————————————————————用法1：老程序改造——————————————————————————————————————
    只要这一句，就可以将原本所有的屏幕输出导出到文件中。
    logger = Lewin_Logging().catch_sys().add_handler_file(path='all_log.txt',  level='all')
    [或者使用默认值，会在 [程序所在目录] 生成log{date}.log文件]
    logger = Lewin_Logging().catch_sys().add_handler_file()
    [或者使用偷懒值，会在 [给定目录] 生成log{date}.log文件]
    logger = Lewin_Logging().catch_sys().add_handler_file("Z:\APMOS\Result\")

    ——————————————————————用法2：新程序使用logging记录分级日志——————————————————————————————————————
    logger = Lewin_Logging().catch_sys()   # 为了读取Exception信息，依然需要截取sys
    logger.add_handler_file(path='all_log.txt', level='all')
    logger.add_handler_stdout(level='all')
    ......
    logger.info("log something")

    ——————————————————————常用format参考——————————————————————————————————————
    "[%(levelname)s]%(datetime)s-%(pathname)s-%(filename)s-%(funcName)s()-%(lineno)d : %(message)s"
    "[%(levelname)s %(time)s] %(message)s"
    "%(message)s"

    ——————————————————————注释——————————————————————————————————————
    <open file object>不需要显式地.close()，python解释器在最后会自动flush+close.
    """

    level_dict = {'all': 0, 'debug': 1, 'info': 2, 'warning': 3, 'error': 4, 'critical': 5}
    fmt = {'simple': "[%(levelname)s] %(message)s",
           'info': "[%(levelname)s][%(time)s] %(message)s",
           'all': "[%(levelname)s][%(time)s][%(filename)s %(funcName)s()][%(processid)s/%(lineno)d][%(loggername)s] %(message)s",
           'debug': "[%(levelname)s][%(time)s][%(filename)s %(funcName)s()][%(processid)s/%(lineno)d] %(message)s",
           'multiprocess': "[%(levelname)s][%(time)s][PID:%(processid)s] %(message)s"}

    __date__ = "2019.04.10"

    def __init__(self, get_stdout=True, get_stderr=True, name=None):
        if name == None:
            name = "%s_%s" % (os.path.basename(sys._getframe(1).f_code.co_filename), time.time())
        self.name = name
        # 把现有的stdout和stderr备份
        stdout, stderr = sys.stdout, sys.stderr
        self.sys_std = {'stdout': stdout, 'stderr': stderr}
        self.handler_packs = []
        # 各种参数/开关
        self.if_do = 0
        self.if_done = False
        self.get_stdout, self.get_stderr = get_stdout, get_stderr
        self.catch_sys(get_stdout, get_stderr)

    def __del__(self):
        if self.if_done:
            return
        try:
            sys.stdout = self.sys_std['stdout']
            sys.stderr = self.sys_std['stderr']
        except:
            pass

    # 懒人方法
    def do(self, function, *args, done=True, **kwargs):
        self.hello()
        # 如果在这里内部执行，那么所有回溯方法(sys._getframe)都要多走一次。
        self.if_do = 1
        # 检查提醒是否将logger输出到屏幕上了，只能用stdout不能用logging方法
        if True not in [pack['file_obj'] == self.sys_std['stdout'] for pack in self.handler_packs]:
            self.sys_std['stdout'].write(
                "[Warning] You haven't add_handler_stdout, loggings will not shown on screen.\n")
        # 开始执行程序
        try:
            function(*args, **kwargs)
        except:
            self.get_except()
        self.if_do = 0
        print("\n\n")
        # 检查是否需要收尾退出
        if done == True:
            self.done()
        else:
            return self

    def hello(self):
        line = "+" * 100 + "\n"
        myfile = os.path.abspath(sys.argv[0])
        mydate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s = line + line + myfile.center(100, '-') + "\n" + mydate.center(100, '-') + "\n" + line + line
        # 在所有handler和stdout输出
        temp_dict = {pack['file_obj']: None for pack in self.handler_packs}
        temp_dict.update({self.sys_std['stdout']: None})
        for obj in temp_dict.keys():
            obj.write(s)
        return self

    def done(self):
        if self.if_done: print("[Warning] logging已经完成了自身的清理，不再重复清理。"); return
        # 邮件对象优先发送
        self.send_handler_email()
        # 还原stdout, stderr
        sys.stdout = self.sys_std['stdout']
        sys.stderr = self.sys_std['stderr']
        self.if_done = True

    def get_except(self, stderr=True):
        import traceback
        except_info = ''.join(traceback.format_exception(*sys.exc_info()))
        if stderr:
            sys.stderr.write(except_info)
            # 这里是Jack对象，因为没有输出到stderr的print所以只能这样写。会直接浮到最顶层，每个Lewin_Logging都会捕获一次。
        else:
            self.critical("Exception!\n" + except_info)

    # 添加hanlder
    def add_handler_stdout(self, level='all', fmt=fmt['simple']):
        get_stdout, get_stderr = False, False  # 不能重复
        return self.add_handler(self.sys_std['stdout'], level, fmt, get_stdout, get_stderr)

    def add_handler_file(self, path="", level='all', fmt=fmt['info'],
                         get_stdout=True, get_stderr=True,
                         dirname="", filename="",
                         backup=0):
        # 默认一天一个日志文件
        default_file = 'log%s.log' % datetime.now().strftime("%Y%m%d")
        default_dir = os.path.dirname(os.path.abspath(sys._getframe(1 + self.if_do).f_code.co_filename))
        path = Lewin_findfiles.easy_path(path, dirname, filename, default_dir, default_file)
        print(default_dir)
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
            print("[Warning] Create dir: %s." % os.path.dirname(path))
        # 只有使用默认文件名才支持
        if backup and (os.path.basename(path) == default_file):
            re_complie = re.compile("log.+?\.log")
            path_dir = os.path.dirname(path)
            path_backup = os.path.join(path_dir, "backup")
            os.mkdir(path_backup) if not os.path.exists(path_backup) else None
            all_list = re_complie.findall(str(os.listdir(path_dir)))
            white_list = ['log%s.log' % (datetime.now() - timedelta(i)).strftime("%Y%m%d") for i in range(backup)]
            black_list = [file for file in all_list if file not in white_list]
            for file in black_list:
                try:
                    os.rename(os.path.join(path_dir, file), os.path.join(path_backup, file))
                except:
                    print("[Warning] Failed to move %s" % os.path.join(path_dir, file))
        elif backup:
            print("[Warning] Won't backup. Only backup files when using default filename like %s." % default_file)
        return self.add_handler(open(path, 'a+', encoding='utf8'), level, fmt, get_stdout, get_stderr)

    def add_handler_eamil(self, email_name="lewin", level='all', fmt=fmt['info'],
                          get_stdout=True, get_stderr=True,
                          subject="", to_addr="", only_when_autorun=False):
        if only_when_autorun:
            if "-autorun" not in sys.argv: return self
        if not subject:
            subject = "%s [Lewin_Logging Report]" \
                      % os.path.basename(sys._getframe(1 + self.if_do).f_code.co_filename)
        if not to_addr:
            to_addr = "lewin.lan@apcapitalinvestment.com"
        obj = Lewin_Logging.Email_Handler(email_name, subject, to_addr)
        return self.add_handler(obj, level, fmt, get_stdout, get_stderr)

    def add_handler_self(self, name="", level='all', fmt=fmt['info'],
                         get_stdout=True, get_stderr=True):
        obj = Lewin_Logging.Self_Handler(name)
        return self.add_handler(obj, level, fmt, get_stdout, get_stderr)

    def add_handler(self, file_obj, level, fmt, get_stdout, get_stderr):
        """handler 可以理解为输出的地方。可以输出在控制台，文件，甚至任何file-object。"""
        # 对将要添加的handler的有效性进行检查
        if level not in Lewin_Logging.level_dict.keys():
            raise Exception("Wrong output level name.")
        for pack in self.handler_packs:
            if file_obj == pack['file_obj']:  # ！！这个条件好像有点问题，重复打开文件的时候并不会报错，貌似也能正常写入
                raise Exception("Duplicate file-object.")
        # 无误，添加handler
        self.handler_packs.append({'file_obj': file_obj, 'level': level, 'fmt': fmt,
                                   'get_stdout': get_stdout, 'get_stderr': get_stderr})
        return self

    # logging方法
    def debug(self, s, titile: str = None, end="\n"):
        self.write('debug', s, titile, end)

    def info(self, s, titile: str = None, end="\n"):
        self.write('info', s, titile, end)

    def warning(self, s, titile: str = None, end="\n"):
        self.write('warning', s, titile, end)

    def error(self, s, titile: str = None, end="\n"):
        self.write('error', s, titile, end)

    def critical(self, s, titile: str = None, end="\n"):
        self.write('critical', s, titile, end)

    def write(self, log_level, s, titile, end):
        dct = {'levelname': log_level.upper(),
               'pathname': sys.argv[0],
               'filename': sys._getframe(2 + self.if_do).f_code.co_filename,
               'funcName': sys._getframe(2 + self.if_do).f_code.co_name,
               'processid': os.getpid(),
               'lineno': sys._getframe(2 + self.if_do).f_lineno,
               'date': datetime.now().strftime('%Y-%m-%d'),
               "datetime": datetime.now().strftime('%Y%m%d%H%M%S'),
               "time": datetime.now().strftime('%H:%M:%S'),
               "exactly_time": str(datetime.now().time()),
               "message": s,
               'loggername': self.name, }
        for pack in self.handler_packs:
            # 判断级别
            handler_nlevel = Lewin_Logging.level_dict[pack['level']]
            log_nlevel = Lewin_Logging.level_dict[log_level]
            if handler_nlevel <= log_nlevel:
                # 准备输出内容
                if titile == None:
                    s = pack['fmt'] % dct + end
                else:
                    s = "%s%s%s" % (titile, s, end)

                pack['file_obj'].write(s)

    # 安排sys.stdout和sys.stderr
    def catch_sys(self, get_stdout, get_stderr):
        jack_out = Lewin_Logging.Jack('stdout', self)
        jack_err = Lewin_Logging.Jack('stderr', self)
        if get_stdout:
            sys.stdout = jack_out
        if get_stderr:
            sys.stderr = jack_err
        return self

    def sys_write(self, name, s):
        s = str(s)
        self.sys_std[name].write(s)
        for pack in self.handler_packs:
            if pack['get_' + name] == True:
                pack['file_obj'].write(s)

    def sys_flush(self, name):
        self.sys_std[name].flush()
        for pack in self.handler_packs:
            if pack['get_' + name] == True:
                pack['file_obj'].flush()

    class Jack:
        """作为替身，截取sys.stdout和stderr
        机制：   当调用print()时，其实解释器调用了sys.stdout.write()
                当raiseException时，其实解释器调用了sys.stderr.write()
        """

        def __init__(self, name, logger):
            self.name = name
            self.logger = logger  # logger是上一级Lewin_Logging对象

        def write(self, s):
            self.logger.sys_write(self.name, s)

        def flush(self):
            self.logger.sys_flush(self.name)

    def send_handler_email(self):
        for pack in self.handler_packs:
            if isinstance(pack['file_obj'], Lewin_Logging.Email_Handler):
                pack['file_obj'].send()

    class Email_Handler:
        def __init__(self, email_name, subject, to_addr):
            if email_name.lower() == 'lewin':
                self.email_obj = LewinEmail()
            elif email_name.lower() == 'mo':
                self.email_obj = LewinEmail_mo()
            else:
                raise Exception("Unsupport Email-name! ")
            self.email_text = ""
            self.subject = subject
            self.to_addr = to_addr
            self.if_send = False

        def write(self, s):
            self.email_text += s

        def flush(self):
            pass

        def close(self):
            if not self.if_send:
                print("[Error] 添加了email_handler，请在程序结束之前，显式地调用logging.send_handler_email()，否则没有发送邮件。")

        def send(self):
            if self.if_send:
                print("[Warning] 已经发送过邮件了，不再发送。请检查你的代码是否有重复的部分。\n",
                      "   [Tips] logging.done()会自动将所有的handler_email发送出去。")
                return
            htmltext = self.email_text.replace('\n', '<br>\n')
            msg = self.email_obj.generate_mimetext_html(self.subject, htmltext, self.to_addr, toname="",
                                                        fromname="")  # 生成MIMEText文本。也可以自己生成。
            self.email_obj.send(self.to_addr, msg)  # 传入一个MIMEText文本，发送邮件。
            self.if_send = True

    def read_handler_self(self, name=None, to_str=True):
        if not name:
            pass
        elif type(name) != type([]):
            name = [name]
        result = []
        for pack in self.handler_packs:
            if isinstance(pack['file_obj'], Lewin_Logging.Self_Handler):
                if (not name) or (pack['file_obj'].name in name):
                    result.append(pack['file_obj'])
        if to_str:
            return "\n\n".join([str(x) for x in result])
        else:
            return result

    def get_handler_self(self):
        for pack in self.handler_packs:
            if isinstance(pack['file_obj'], Lewin_Logging.Self_Handler):
                return pack['file_obj']

    class Self_Handler:
        def __init__(self, name):
            self.s = ""
            if not name:
                name = "default"
            self.name = name

        def write(self, s):
            self.s += s

        def flush(self):
            pass

        def __str__(self):
            return self.s

        def to_html(self):
            import html
            html_logging = self.s
            html_logging = html.escape(html_logging).replace("\n", "<br>").replace(" ", "&nbsp;")
            html_logging = html_logging.replace("[DEBUG]", "<font color='green'>[DEBUG]</font>")
            html_logging = html_logging.replace("[INFO]", "<font color='blue'>[INFO]</font>")
            html_logging = html_logging.replace("[WARNING]", "<font color='orange'>[WARNING]</font>")
            html_logging = html_logging.replace("[ERROR]", "<font color='red'>[ERROR]</font>")
            html_logging = html_logging.replace("Traceback (most recent call last):",
                                                "<font color='red'><b>Traceback (most recent call last):</b></font>")
            return html_logging

        def clear(self):
            self.s = ""


class Easy_Logging:
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


class Easy_Logging_Time:
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


class Easy_Jack:
    """
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
