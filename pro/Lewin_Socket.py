#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
__all__ = ['Lewin_Socket_Server', "Lewin_Socket_Client"]
"""

"""

import os, sys, socket, struct
from socket import socket
import socket as Socket
from LewinTools.common.Lewin_Logging import Easy_Logging_Time, Lewin_Logging


# ————————————————————————————————————————————————————————


class _Base_Socket:
    __date__ = "2019.04.11"

    def __init__(self, logger: Lewin_Logging = None):
        self.over_Buffer = b''
        self.logger = Easy_Logging_Time()
        if logger == None:
            self.logger = Easy_Logging_Time()
        else:
            self.logger = logger
        self._init_settings()

    def _init_settings(self):
        self.settings = {"headerSize": 8, }

    def recv(self, conn: socket):
        dataBuffer = b''
        while True:
            # 如果有上次的粘包，那就不recv了。
            if self.over_Buffer:
                data = self.over_Buffer
                self.over_Buffer = b''
            else:
                data = conn.recv(1024)
            if data:
                # 把数据存入缓冲区，类似于push数据
                dataBuffer += data
                while dataBuffer:
                    if len(dataBuffer) < self.settings["headerSize"]:
                        self.logger.error("received a pack（%s）which is too small, skiped" % dataBuffer)
                        return ""
                    # read header
                    command, bodySize = struct.unpack('!II', dataBuffer[:self.settings["headerSize"]])
                    wholeSize = self.settings["headerSize"] + bodySize
                    if len(dataBuffer) < wholeSize:
                        # 分包处理
                        self.logger.debug("incomplete pack, break to receive next.")
                        break
                    # pop处理一个包，如果有粘包就先储存着，下一次访问本函数的时候会读取到。
                    self.over_Buffer = dataBuffer[wholeSize:]
                    return dataBuffer[self.settings["headerSize"]:wholeSize].decode()
            else:
                return ""

    def send(self, conn: socket, body: str, command: int = 200):
        header = struct.pack('!II', command, len(body))
        conn.sendall(header + body.encode())


class Lewin_Socket_Server(_Base_Socket):
    """
    pls inherit Lewin_Socket_Server,
    choice 1:
        overwrite "with_conn(self, conn:socket, addr:str)" and even "run_server".
    choice 2:
        add a "backend(self, conn:socket, recv_data:str)".
    """
    __date__ = "2019.04.11"

    def run_server(self, host="", port=8012):
        with socket() as s:
            s.bind((host, port))
            s.listen(1)
            while True:
                self.logger.info("listening at %s:%s" % (Socket.gethostbyname(Socket.gethostname()), port))
                conn, addr = s.accept()
                with conn:
                    self.with_conn(conn, addr)

    def with_conn(self, conn: socket, addr: str):
        self.logger.info("Connected from %s" % (addr,))
        recv_data = self.recv(conn)
        print("backend function received: %s" % recv_data)


class Lewin_Socket_Client(_Base_Socket):
    """
    pls inherit Lewin_Socket_Client,
    and overwrite "with_conn(self, conn:socket)" or even overwrite "login".
    """
    __date__ = "2019.04.10"

    def login_run(self, host: str, port: int):
        with socket() as conn:
            conn.connect((host, port))
            self.with_conn(conn)

    def with_conn(self, conn: socket):
        body = "hello!"
        self.send(conn, body)
