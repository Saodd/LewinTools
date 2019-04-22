#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys, re
from datetime import datetime


# ————————————————————————————————————————————————————————
class Lewin_Outbox:
    __date__ = "2019.04.12"

    def __init__(self):
        """        会从当前目录读取配置文件lewin_config.py        """
        from email.mime.text import MIMEText
        from email.header import Header
        from email.utils import parseaddr, formataddr
        self.MIMEText = MIMEText
        self.Header = Header
        self.parseaddr = parseaddr
        self.formataddr = formataddr

    def __del__(self):
        # 有的时候会报错：smtplib.SMTPServerDisconnected: Server not connected，所以让它自生自灭吧
        try:
            self.server.quit()
        except:
            pass

    def login(self, account, password, server_addr, server_port=465, name=""):
        """手动设置发件人的邮箱账号、密码、姓名。（用于登录邮箱服务器）"""
        self.FROM_ADDR = account
        self.FROM_ADDR_PASSWORD = password
        if name:
            self.FROM_NAME = name
        else:
            self.FROM_NAME = account.split("@")[0]
        print("set from-email as %s, from-name as %s" % (account, name))
        import smtplib
        self.server = smtplib.SMTP_SSL(server_addr, server_port)
        self.server.login(self.FROM_ADDR, self.FROM_ADDR_PASSWORD)

    def generate_mimetext_html(self, subject, htmltext, to_addr, toname="", fromname=""):
        """传入to_addr可以是str，也可以是list。
        返回一个'MIMEText'对象，可以作为参数传递给send()，也可以用在别的地方。"""
        to_addr = self._exam_list(to_addr)
        # 设置邮件正文、标题、发件人、收件人
        msg = self.MIMEText('<html><body>%s</body></html>' % (htmltext,), 'html', 'utf-8')
        msg['Subject'] = self.Header(subject, 'utf-8').encode()
        if not fromname:
            fromname = self.FROM_NAME
        msg['From'] = self._format_addr('%s <%s>' % (fromname, self.FROM_ADDR))
        if len(to_addr) == 1:
            msg['To'] = self._format_addr('%s <%s>' % (toname, to_addr[0]))
        else:
            msg['To'] = ','.join(to_addr)
        return msg

    def send(self, to_addr, msg):
        """传入的参数msg必须是'MIMEText'对象。可以是从本类的方法中生成的，也可以是自定义的。
        传入to_addr可以是str，也可以是list。
        """
        to_addr = self._exam_list(to_addr)
        self.server.sendmail(self.FROM_ADDR, to_addr, msg.as_string())
        print("[INFO] Email sent to ", to_addr)

    def _format_addr(self, s):
        """需要中文发件人/收件人的话，就必须通过这个方法编码，否则邮件中显示乱码"""
        name, addr = self.parseaddr(s)
        if not name:
            name = addr.split("@")[0]
        return self.formataddr((self.Header(name, 'utf-8').encode(), addr))

    def _exam_list(self, arg):
        if type(arg) == type([]):
            return arg
        else:
            return [arg]


# ————————————————————————————————————————————————————————
class Lewin_Inbox:
    pass
