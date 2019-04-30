#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/30'
"""

"""

import os, sys

# ———————————————————————环境变量—————————————————————————————————
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if path not in sys.path:
    sys.path.insert(0, path)
from LewinTools.common.Lewin_Logging import Easy_Logging_Time
from LewinTools.pro.Lewin_Email import Lewin_Outbox
from LewinTools.password import Mail163 as Email_Account

# ————————————————————————— Functions ———————————————————————————————
def test__send_text_email():
    __date__ = "2019.04.30"
    logger = Easy_Logging_Time()
    outbox = Lewin_Outbox(logger)
    outbox.login_ssl(**Email_Account)
    msg = outbox.write_MIMEtext_text("Test email!", "I'm testing my module!", Email_Account["account"], Email_Account["name"])
    outbox.send_MIMEtext(Email_Account["account"], msg)

# ————————————————————————— run ———————————————————————————————
if __name__ == '__main__':
    test__send_text_email()
