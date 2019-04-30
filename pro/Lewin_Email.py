#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys
from typing import Union, List
import smtplib
from email.mime.text import MIMEText

# ———————————————————————环境变量—————————————————————————————————
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if path not in sys.path:
    sys.path.insert(0, path)
from LewinTools.common.Lewin_Logging import Logging_Mute
from email.header import Header
from email.utils import formataddr


# ————————————————————————————————————————————————————————
class Lewin_Outbox:
    __date__ = "2019.04.30"

    def __init__(self, logger=None):
        if logger is None:
            self.logger = Logging_Mute()
        else:
            self.logger = logger

    def __del__(self):
        # 有的时候会报错：smtplib.SMTPServerDisconnected: Server not connected，所以让它自生自灭吧
        try:
            self.server.quit()
        except:
            pass

    def login_ssl(self, account: str, password: str, server_addr: str, server_port=465, name="") -> bool:
        """手动设置发件人的邮箱账号、密码、姓名。（用于登录邮箱服务器）"""
        self.from_account = account
        self.from_password = password
        self.from_name = name if name else account.split("@")[0]
        self.logger.info("Set email: %s. Set name: %s." % (account, name))
        try:
            self.server = smtplib.SMTP_SSL(server_addr, server_port)
            self.server.ehlo()
            self.server.login(account, password)
        except Exception as e:
            self.logger.error("Failed when login email server: %s." % e)
            raise
        else:
            return True

    def write_MIMEtext_html(self, subject: str, htmltext: str, to_account: Union[str, List[str]],
                            from_name="") -> MIMEText:
        """传入to_addr可以是str，也可以是list。
        返回一个'MIMEText'对象，可以作为参数传递给send()，也可以用在别的地方。"""
        to_account = self._list(to_account)
        if not from_name:
            from_name = self.from_name
        # 设置邮件正文、标题、发件人、收件人
        msg = MIMEText('<html><body>%s</body></html>' % htmltext, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = formataddr((Header(from_name, 'utf-8').encode(), self.from_account))
        msg['To'] = ','.join(to_account)
        return msg

    def write_MIMEtext_text(self, subject: str, text: str, to_account: Union[str, List[str]],
                            from_name="") -> MIMEText:
        to_account = self._list(to_account)
        if not from_name:
            from_name = self.from_name
        msg = MIMEText(text, 'plain', 'utf-8')  # different
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = formataddr((Header(from_name, 'utf-8').encode(), self.from_account))
        msg['To'] = ','.join(to_account)
        return msg

    def send_MIMEtext(self, to_account: Union[str, List[str]], msg: MIMEText) -> bool:
        """传入的参数msg必须是'MIMEText'对象。可以是从本类的方法中生成的，也可以是自定义的。
        传入to_addr可以是str，也可以是list。
        """
        to_account = self._list(to_account)
        try:
            self.server.sendmail(self.from_account, to_account, msg.as_string())
        except Exception as e:
            self.logger.error("Failed when login email server: %s." % e)
            raise
        else:
            self.logger.info("Email sent to %s" % to_account)
            return True

    def _list(self, arg: Union[str, List[str]]) -> list:
        if type(arg) == type([]):
            return arg
        else:
            return [arg]


# ————————————————————————————————————————————————————————
class Lewin_Inbox:
    pass
