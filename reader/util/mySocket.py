# -*- coding: UTF-8 -*-
import __init__
import re
import struct
import threading
import datetime
import socket
import time
import traceback

from novelweb.baidu import Baidu


# 最简单的自定义异常
class FError(Exception):
    pass


class MySocket:
    # 数据类型
    # $1,xxxxxxxxxx
    # 第二位即为数据类型
    dataType_bookList = 1  # 书单
    dataType_chapterContent = 2  # 小说内容
    dataType_progress = 3  # 进度
    dataType_chapterNum = 4  # 章节数
    dataType_bookSize = 5  # 小说大小
    dataType_error = 6  # 爬取出错
    dataType_info = 7  # 消息
    dataType_downloadProgress = 8  # 下载进度
    dataType_bookName = 9  # 书籍名称

    def __init__(self, *args):
        if len(args) == 1:
            self.port = args[0]
            self.listenLock = threading.Lock()
            self.listenLock.acquire()
            self.MAX_CLIENT = 5  # 最大可同时连接5个客户端py
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 关闭端口后立即释放该端口
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 保持连接状态
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)  # 设置发送缓冲区大小
            # print(self.serverSocket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
            # print(self.serverSocket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
            self.serverSocket.bind(('', self.port))
            self.serverSocket.listen(self.MAX_CLIENT)
            self.currentSock = None
            self.currentSockAddr = None
            self.loginSockList = []
            self.loginSockAddrList = []
            print(datetime.datetime.now().strftime('%H:%M:%S') + '创建服务器成功 监听端口号:' + self.port.__str__())
        elif len(args) == 0:
            pass

    # 等待客户端连接
    def waitSocketConnectThread(self):
        while True:
            self.currentSock, self.currentSockAddr = self.serverSocket.accept()
            print(datetime.datetime.now().strftime('%H:%M:%S') + str(self.currentSockAddr) + "连接至服务器")
            threading.Thread(target=self.login, args=(self.currentSock, self.currentSockAddr)).start()

    def login(self, sock, sockAddr):
        loginFlag = True
        if loginFlag:
            sock.settimeout(5)
            try:
                buff = sock.recv(1024).decode("gbk")
                if len(buff) > 0:
                    if buff[0] == '$' and buff[-1] == '#':  # 收到正确命令
                        if buff[1] == '-':  # 登录命令 "$-#"
                            self.loginSockList.append(sock)
                            self.loginSockAddrList.append(sockAddr)
                            self.listenLock_release()
                            sock.settimeout(None)
                            print(datetime.datetime.now().strftime('%H:%M:%S') + str(sockAddr) + "登录成功")
            except:
                print(datetime.datetime.now().strftime('%H:%M:%S') + str(sockAddr) + "登录超时")
        else:
            print(datetime.datetime.now().strftime('%H:%M:%S') + str(sockAddr) + "登录成功")
            self.loginSockList.append(sock)
            self.loginSockAddrList.append(sockAddr)
            self.listenLock_release()

    def listenLock_release(self):
        try:
            self.listenLock.release()
        except:
            pass

    # 按照格式通过socket发送数据
    def socketSendData(self, sock, dataType, data):
        contentData = data.encode()
        headLen = len('$1,xxxxxxxxxx,')  # $xxxxxxxxxx,1,
        headData = '$%d,%.10d,' % (dataType, len(contentData) + headLen)
        # print('数据长度' + str(len(contentData) + headLen))
        totalData = headData.encode() + contentData
        totalLen = len(headData.encode() + contentData)
        sent = 0
        try:
            while sent < totalLen:  # 因为可能一次性发送不了全部的字节 故可能需多次发送
                sent += sock.send(totalData[sent:totalLen])
        except:
            pass
