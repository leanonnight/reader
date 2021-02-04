# -*- coding: UTF-8 -*-
import platform
import struct
import zlib

import psutil

import __init__
import datetime
import math
import os
import re
import socket
import time
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process, Queue, Lock, Manager
import multiprocessing
import requests
from bs4 import UnicodeDammit
from bs4 import BeautifulSoup


from util.myUtil import reformChapterName
from novelweb.baidu import Baidu
from novelweb.universalNovelweb import Novelweb
from novelweb.mianhuatang import MianHuaTang
from util.mySocket import MySocket


class HandleProcess(Process):
    # 命令类型
    cmdType_SearchBook = '1'  # 搜索书籍命令
    cmdType_ParseUrl = '2'  # 解析小说主页命令
    cmdType_Quit = '3'  # 停止
    cmdType_Exit = '4'  # 退出当前进程
    cmdType_Restart = '5' # 重启程序

    # def getProcessRunTime(self):
    #     nowTime = time.time()
    #     print((round((nowTime - self.startTime))).__str__())

    # def getMessage(self, process):
    #     pid = process.pid
    #     p = psutil.Process(pid)
    #     return {
    #         '进程编号': pid.__str__(),
    #         '进程名称': p.name().__str__(),
    #         '执行路径': p.exe().__str__(),
    #         '当前路径': p.cwd().__str__(),
    #         '启动命令': p.cmdline().__str__(),
    #         '父进程ID': p.ppid().__str__(),
    #         '父进程': p.parent().__str__(),
    #         "子进程列表": p.children().__str__(),
    #         '状态': p.status().__str__(),
    #         '进程用户名': p.username().__str__(),
    #         '进程创建时间': p.create_time().__str__(),
    #         # '终端': p.terminal().__str__(),
    #         '执行时间': p.cpu_times().__str__(),
    #         '内存信息': p.memory_info().__str__(),
    #         '打开的文件': p.open_files().__str__(),
    #         '相关网络连接': p.connections().__str__(),
    #         '线程数': p.num_threads().__str__(),
    #         '线程': p.threads().__str__(),
    #         '环境变量': p.environ().__str__(),
    #     }

    def __init__(self, id, sock, addr):
        # 初始化父类方法
        Process.__init__(self)
        self.id = id
        self.sock = sock
        self.addr = addr
        self.startTime = time.time()
        self.cmdType = 0  # 命令类型
        self.cmdLock = Lock()  # 先获取命令锁 再判断命令类型
        self.cmdLock.acquire()  # 先锁住
        self.sockLock = Lock()  # socket锁
        self.keyword = ""  # 搜索关键词
        self.recv_url = ""  # 小说主页url
        self.currentProcess = None  # 当前程序执行的进程
        self.initTime = None
        self.mySocket = MySocket()  # 用来调用socketSendData()方法
        self.novelWeb = Novelweb()  # 用来解析网站
        print(datetime.datetime.now().strftime('%H:%M:%S') + "process id = %d start" % self.id)

    def socket_sendData(self, dataType, data):
        self.sockLock.acquire()
        try:
            self.mySocket.socketSendData(self.sock, dataType, data)
        except:
            traceback.print_exc()
        finally:
            self.sockLock.release()

    def run(self):
        threading.Thread(target=self.socket_recvData_thread).start()  # 开启接收数据线程
        while True:  # 收到命令后释放锁 然后才能获取命令 进而根据命令类型做进一步操作（为了不让系统在while循环中浪费Cpu资源，而让该线程阻塞在这里）
            try:  # 长时间未获取锁会超时
                self.cmdLock.acquire()
                if self.cmdType == self.cmdType_SearchBook:
                    self.cmdType = 0
                    # 开启搜索书籍进程
                    self.currentProcess = Process(target=self.search_book_process, args=(self.keyword,))
                    self.currentProcess.start()
                elif self.cmdType == self.cmdType_ParseUrl:
                    self.cmdType = 0
                    # 开启解析书籍主页url的进程
                    self.currentProcess = Process(target=self.parse_url_process, args=(self.recv_url,))
                    self.currentProcess.start()
                elif self.cmdType == self.cmdType_Quit:
                    print("cmdType == cmdType_Quit")
                    self.cmdType = 0
                    if self.currentProcess is not None:
                        self.currentProcess.kill()
                        self.currentProcess = None
                    else:
                        self.socket_sendData(MySocket.dataType_info, "当前无正在执行进程")
                elif self.cmdType == self.cmdType_Exit:
                    print("cmdType == cmdType_Exit")
                    if self.currentProcess is not None:
                        self.currentProcess.kill()
                        self.currentProcess = None
                    break
                elif self.cmdType == self.cmdType_Restart:
                    print("cmdType == cmdType_Restart")
                    os.system("sh restart.sh")
            except:
                traceback.print_exc()
        print(datetime.datetime.now().strftime('%H:%M:%S ') + "process id = %d end" % self.id)

    # 定时线程
    def timer_thread(self, timerLock, timerEndLock, timeInterval):
        timerEndLock.acquire()
        while True:
            try:
                time.sleep(timeInterval)
                timerLock.release()
                if timerEndLock.acquire(False):  # 如果能获取定时结束锁 则定时线程结束
                    break
            except:  # 忽略重复释放锁错误
                pass

    def socket_recvData_thread(self):
        while True:
            try:
                buff = self.sock.recv(1024).decode("gbk")
                if len(buff) > 0:
                    print(buff)
                    if buff[0] == '$' and buff[-1] == '#':  # 收到正确命令
                        if buff[1] == self.cmdType_SearchBook:  # 收到请求查询命令
                            # sock.send("正在查询请稍后...".encode("gbk"))
                            keyword = buff[3:-1]
                            print("keyword:" + keyword)
                            self.keyword = keyword
                            self.cmdType = self.cmdType_SearchBook
                        elif buff[1] == self.cmdType_ParseUrl:  # 响应 客户端告知需要下载的书籍的主页Url 格式 $2,url,#
                            cmds = buff.split(',')
                            url = cmds[1]
                            print('url:' + url)
                            self.recv_url = url
                            self.cmdType = self.cmdType_ParseUrl
                        elif buff[1] == self.cmdType_Quit:  # 停止当前进程 格式 $3#
                            self.cmdType = self.cmdType_Quit
                        elif buff[1] == self.cmdType_Restart:  # 重启当前进程 格式 $3#
                            self.cmdType = self.cmdType_Restart
                        self.cmdLock.release()  # 收到命令 释放锁
                else:
                    break
            except:
                traceback.print_exc()
                break
        print(datetime.datetime.now().strftime('%H:%M:%S') + str(self.addr) + "断开连接")
        self.sock.close()
        self.cmdType = self.cmdType_Exit
        self.cmdLock.release()  # 收到命令 释放锁

    # 搜索书籍进程
    def search_book_process(self, keyword):
        for result in self.novelWeb.search_book(keyword):
            self.socket_sendData(MySocket.dataType_info, result["webName"] + ":" + str(len(result["resultList"])))
            self.socket_sendData(MySocket.dataType_bookList, str(result))

    # 解析小说主页进程
    def parse_url_process(self, recv_url):
        try:
            print('--------------start crawl book--------------------')
            self.socket_sendData(MySocket.dataType_info, '---start crawl book---')
            startTime = time.time()

            ########################################################
            # 解析主页 返回章节名列表、章节url列表、书籍主域名、书名、网站主域名
            ########################################################
            chapterNameList, chapterUrlList, base_domain, bookName, web_domain, chapterNum = self.novelWeb.parse_homeUrl(
                url=recv_url)
            urlNum = len(chapterUrlList)  # 求url数量
            # urlNum = 100
            self.socket_sendData(MySocket.dataType_chapterNum, str(urlNum))
            self.socket_sendData(MySocket.dataType_info, "小说" + "共%d章" % chapterNum + " 需请求的url数量:%d" % urlNum)
            print("小说" + "共%d章" % chapterNum + " 需请求的url数量:%d" % urlNum)

            ########################################
            # 改造章节名 改为能被小说软件识别的章节名
            ########################################
            reformChapterName(urlNum, chapterNameList)

            ####################################################
            # 创建一个与url数大小一致的列表 用于存储小说章节内容
            ####################################################
            chapterContentList = Manager().list()  # 章节内容列表
            chapterUrlsList = []  # url列表
            for i in range(urlNum):
                chapterContentList.append('')

            ########################################
            #  创建进程安全队列
            ########################################
            urlQueue = Manager().Queue(urlNum)  # url队列
            htmlContentQueue = Manager().Queue(urlNum)  # requests获取的原生html和url
            chapterQueue = Manager().Queue(urlNum)  # 章节队列
            productSemaphore = Manager().Queue(urlNum)  # 信号量 用来计算还有多少个html未获取

            # ########################################
            # # 创建与url数大小一致的信号量
            # ########################################
            for i in range(urlNum):
                productSemaphore.put('')

            ########################################
            #  构建chapterUrls
            ########################################
            for x in range(urlNum):
                url = base_domain + chapterUrlList[x]
                chapterUrlsList.append(url)
                urlQueue.put(url)

            ########################################
            #  开启解析小说html页面 获取小说章节内容
            ########################################
            timerLock = Lock()
            timerEndLock = Lock()
            remainNum = multiprocessing.Value('i', urlNum)  # 尚未获取的url数量
            # 定时线程
            threading.Thread(target=self.timer_thread, args=(timerLock, timerEndLock, 0.1)).start()
            parseBookHtmlEndLock = Lock()
            parseBookHtmlEndLock.acquire()
            parsedNum = multiprocessing.Value('i', 0)  # 已经解析的数量
            processNum = os.cpu_count()  # 进程数量 等于CPU数量
            print("cpu核心数:" + str(processNum))
            self.socket_sendData(MySocket.dataType_info, "cpu核心数:" + str(processNum))
            self.socket_sendData(MySocket.dataType_info, "正在启动解析html进程...")
            for i in range(processNum):
                Process(target=self.parse_chapterHtml_process, args=(
                htmlContentQueue, remainNum, chapterContentList, chapterUrlsList, timerLock, timerEndLock, parsedNum,
                parseBookHtmlEndLock, self.novelWeb)).start()
            self.socket_sendData(MySocket.dataType_info, "启动解析html进程成功")

            ########################################
            #  开启爬虫线程 获取小说html页面
            ########################################
            if web_domain == self.novelWeb.webDomain_biquge_info:
                sleepTime = 0.5  # 每获取一个url需要延时时间
                threadNum = 100
            elif web_domain == self.novelWeb.webDomain_piaotian:
                sleepTime = 0
                threadNum = int(int(urlNum))
            elif web_domain == self.novelWeb.webDomain_piaotian:
                sleepTime = 1
                threadNum = 100
            else:
                sleepTime = 0
                threadNum = int(int(urlNum))
            print("线程数:%d" % threadNum)
            print("每获取一个url需要延时时间:%d" % sleepTime)
            threadPool = ThreadPoolExecutor(max_workers=threadNum)
            self.initTime = time.time()
            timerLock = Lock()
            timerEndLock = Lock()
            # 定时线程
            self.socket_sendData(MySocket.dataType_info, "正在启动爬虫...")
            threading.Thread(target=self.timer_thread, args=(timerLock, timerEndLock, 0.1)).start()
            for y in range(threadNum):
                time.sleep(sleepTime)
                threadPool.submit(self.crawl_book_thread, y, urlQueue, htmlContentQueue, remainNum, timerLock,
                                  timerEndLock, sleepTime)
            self.socket_sendData(MySocket.dataType_info, "全部爬虫启动完成 共启动" + str(threadNum) + "只爬虫")

            self.socket_sendData(MySocket.dataType_info, "开始全速解析html")           
            # 等待解析小说html页面的进程完成
            parseBookHtmlEndLock.acquire()
            # MySocket().socketSendData(sock, MySocket.dataType_progress, str(times))  # 发送最后一次进度
            print("爬取完成！此次爬取用时:" + (round((time.time() - startTime) * 1000)).__str__() + "ms")
            ########################################
            # 保存到本地
            ########################################
            time1 = time.time()
            print('文件名:' + bookName)
            print("章节数:" + str(len(chapterContentList)))
            self.novelWeb.save_book(bookName, chapterNameList, chapterContentList)
            print("《%s》写入完成用时:" % bookName + (round((time.time() - time1) * 1000)).__str__() + "ms")
            self.socket_sendData(MySocket.dataType_info,
                                 "《%s》写入完成用时:" % bookName + (
                                     round((time.time() - time1) * 1000)).__str__() + "ms")
            with open("%s.txt" % bookName, 'rb') as f:
                self.socket_sendData(MySocket.dataType_info, "《%s》开始发送" % bookName)
                print("《%s》开始发送" % bookName)
                self.socket_sendData(MySocket.dataType_bookName, bookName)
                # 发送爬下来的书籍
                f.seek(0)
                bookByte = f.read()
                time.sleep(0.1) # 防止粘包
                compress = zlib.compressobj(level=9, memLevel=9)
                compressData = compress.compress(bookByte)
                self.socket_sendData(MySocket.dataType_chapterContent, compressData)
                print("《%s》发送完成" % bookName)
                print("\r\n\r\n")
        except Exception as e:
            traceback.print_exc()
            self.socket_sendData(MySocket.dataType_error, repr(e))

    #  爬取小说线程（发送requests请求 然后获取页面html）
    def crawl_book_thread(self, id, urlQueue, htmlContentQueue, remainNum, timerLock, timerEndLock, sleepTime):
        timeoutFlag = False
        re_requested_url = ""  # 记录需要重新发起的url
        while True:
            if not timeoutFlag:  # 如果请求未超时 则开始发起下一个请求
                try:
                    url = urlQueue.get(False)
                except:
                    break
            else:  # 如果请求超时 则重复发起请求
                url = re_requested_url
            try:
                time.sleep(sleepTime)
                # print(url)
                if MianHuaTang.web_domain in url:   # 如果在棉花糖爬取
                    r = requests.get(url=url, timeout=5, headers=MianHuaTang.request_headers)
                else:
                    r = requests.get(url=url, timeout=5)
                timeoutFlag = False
                # 自动选择合适的编码方式
                dammit = UnicodeDammit(r.content, ["utf-8", "gbk"])
                html = dammit.unicode_markup
                #  放入章节内容队列
                htmlContentQueue.put({'html': html, 'url': r.url})
                with remainNum.get_lock():
                    remainNum.value -= 1
                if remainNum.value == 0:
                    self.socket_sendData(MySocket.dataType_info, "还剩余0响应")
                    timerEndLock.release()  # 释放定时结束锁 关闭定时器
                # print("id = %d还剩余%d个响应" % (id, remainNum.value))
            except Exception as e:  # requests请求超时 重新发起请求
                # traceback.print_exc()
                # print(repr(e))
                # 重新发送请求
                timeoutFlag = True
                re_requested_url = url

            if timerLock.acquire(False):  # 获取到定时器锁 则说明定时时间到
                self.socket_sendData(MySocket.dataType_info, "还剩余" + str(remainNum.value) + "响应")

        # print("id:" + str(id) + "  activeCount" + str(threading.activeCount()))

    # 解析章节html进程
    def parse_chapterHtml_process(self, htmlQueue, remainNum, chapterContentList, chapterUrlsList, timerLock,
                                  timerEndLock, parsedNum, parseBookHtmlEndLock, novelWeb):
        while True:
            try:
                content = htmlQueue.get(False)  # 尝试获取html内容
            except:  # 如果没有获取到
                if remainNum.value == 0:  # 如果解析信号量为空并且也没有获取到html内容 则说明解析完成
                    if parsedNum.value == len(chapterContentList):  # 最后一个退出进程的才释放定时器和释放解析结束锁
                        self.socket_sendData(MySocket.dataType_progress, str(parsedNum.value))
                        timerEndLock.release()
                        parseBookHtmlEndLock.release()
                    break
                else:
                    continue
            try:
                html = content['html']
                chapterContent = novelWeb.parse_chapterHtml(html)  # 解析章节html
                chapterContentList[chapterUrlsList.index(content['url'])] = chapterContent
                with parsedNum.get_lock():  # 更新已解析html的数量
                    parsedNum.value += 1
                # print("已爬取%d章节" % parsedNum.value)
                if timerLock.acquire(False):  # 获取到定时器锁 则说明定时时间到
                    self.socket_sendData(MySocket.dataType_progress, str(parsedNum.value))
            except:
                traceback.print_exc()


def start():
    print("start run...")

    mySocket = MySocket(9999)  # 监听端口
    threading.Thread(target=mySocket.waitSocketConnectThread).start()
    id = 1
    while True:
        try:
            # 每当有客户端连接服务器 就开启一个单独的处理进程
            mySocket.listenLock.acquire()
            num = len(mySocket.loginSockList)
            for i in range(num):
                sock = mySocket.loginSockList.pop()
                sockAddr = mySocket.loginSockAddrList.pop()
                HandleProcess(id, sock, sockAddr).start()
            id += 1
        except:
            pass

if __name__ == '__main__':
    start()
