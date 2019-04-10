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
class Settings:
    # header = <1 int: command> + <1 int: body_length>  # command: 200:OK, 999:shutdown
    headerSize = 8

class _Default:
    @staticmethod
    def backend(conn:socket, input:str):
        print(input)
        output = {}
        return output

class _Base_Socket:
    def __init__(self, logger:Lewin_Logging=None):
        self.over_Buffer = b''
        self.logger = Easy_Logging_Time()
        if logger == None:
            self.logger = Easy_Logging_Time()
        else:
            self.logger = logger

    def recv(self, conn:socket):
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
                    if len(dataBuffer) < Settings.headerSize:
                        self.logger.error("received a pack（%s）which is too small, skiped" % dataBuffer)
                        return ""
                    # read header
                    command, bodySize = struct.unpack('!II', dataBuffer[:Settings.headerSize])
                    wholeSize = Settings.headerSize + bodySize
                    if len(dataBuffer) < wholeSize:
                        # 分包处理
                        self.logger.debug("incomplete pack, break to receive next.")
                        break
                    # pop处理一个包，如果有粘包就先储存着，下一次访问本函数的时候会读取到。
                    self.over_Buffer = dataBuffer[wholeSize:]
                    return dataBuffer[Settings.headerSize:wholeSize].decode()
            else:
                return ""


    def send(self, conn:socket, body:str, command:int=200):
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
    def run_server(self, host="", port=8012):
        with socket() as s:
            s.bind((host, port))
            s.listen(1)
            while True:
                self.logger.info("listening at %s:%s"%(Socket.gethostbyname(Socket.gethostname()), port))
                conn, addr = s.accept()
                with conn:
                    self.with_conn(conn, addr)

    def with_conn(self, conn:socket, addr:str):
        self.logger.info("Connected from %s" % (addr,))
        recv_data = self.recv(conn)
        if recv_data:
            if hasattr(self, "backend"):
                self.backend(conn, recv_data)
            else:
                self.logger.warning("no backend function! use test function.")
                _Default.backend(conn, recv_data)




class Lewin_Socket_Client(_Base_Socket):
    """
    pls inherit Lewin_Socket_Client,
    and overwrite "with_conn(self, conn:socket)" or even overwrite "login".
    """
    def login_run(self, host:str, port:int):
        with socket() as conn:
            conn.connect((host, port))
            self.with_conn(conn)

    def with_conn(self, conn:socket):
        body = "hello!"
        self.send(conn, body)
