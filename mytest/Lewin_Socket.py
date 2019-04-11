#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys
from socket import socket

PATH_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PATH_root not in sys.path:
    sys.path.append(PATH_root)

if sys.platform == 'linux':
    from LewinTools.pro.Lewin_Socket import Lewin_Socket_Server
    class MyServer(Lewin_Socket_Server):
        def with_conn(self, conn:socket, addr:str):
            print(self.recv(conn))
            self.send(conn, "hahaha 1, Im server." + "-"*1000)
            print(self.recv(conn))
            self.send(conn, "hahaha 2, Im server.")

    MyServer().run_server()

elif sys.platform == 'win32':
    from LewinTools.pro.Lewin_Socket import Lewin_Socket_Client
    class MyClient(Lewin_Socket_Client):
        def with_conn(self, conn:socket):
            self.send(conn, "hahaha 1, Im client." + "-"*1000)
            print(self.recv(conn))
            self.send(conn, "hahaha 2, Im client.")
            print(self.recv(conn))

    MyClient().login_run("10.1.10.116", 8012)
