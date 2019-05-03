#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys
import socket
from threading import Thread

# ———————————————————————环境变量—————————————————————————————————
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)
from lewintools.pro.socket import Socket_Server, Socket_Client


# ——————————————————————— Functions —————————————————————————————————
class Test__Socket:
    @staticmethod
    def main(): # 运行后请手动结束，否则server会一直等待下去。
        ts = [Thread(target=Test__Socket.test__server), Thread(target=Test__Socket.test__client)]
        [t.start() for t in ts]

    @staticmethod
    def test__server():
        class MyServer(Socket_Server):
            def with_conn(self, conn: socket.socket, addr: str):  # 这个是建立socket之后自动调用的方法，重写使用
                print(self.recv(conn))
                self.send(conn, "hahaha 1, Im server." + "-" * 1000)
                print(self.recv(conn))
                self.send(conn, "hahaha 2, Im server.")

        MyServer().run_server(port=8012)

    @staticmethod
    def test__client():
        class MyClient(Socket_Client):
            def with_conn(self, conn: socket.socket):  # 这个是建立socket之后自动调用的方法，重写使用
                self.send(conn, "hahaha 1, Im client." + "-" * 1000)
                print(self.recv(conn))
                self.send(conn, "hahaha 2, Im client.")
                print(self.recv(conn))

        MyClient().login_run(socket.gethostbyname(socket.gethostname()), 8012)


# ————————————————————————————————————————————————————————
if __name__ == '__main__':
    Test__Socket.main()