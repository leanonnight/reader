# -*- coding: UTF-8 -*-
import sys
import threading
sys.path.append(r'/home')
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

from novelweb.baidu import Baidu
from novelweb.bayizhongwen import BaYiZhongWen
from novelweb.dingdian import DingDian
from novelweb.piaotianwenxue import PiaoTianWenXue

import time

from bs4 import BeautifulSoup

from util.myRequests import MyRequests
import re
from util.util import remove_duplicate_part_of_string, FError


class Novelweb:

    webDomain_biquge_info = "www.biquge.info"
    webDomain_piaotian = "www.piaotian.org"
    webDomain_dingdian = "www.x23us.com"
    webDomain_bayi = "www.zwdu.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 "
                     "Safari/537.36 "
    }

    def __init__(self):
        self.base_url = ""  # 小说主页基url
        self.web_domain = ""  # 小说网站主域名
        self.chapterNameList = []
        self.chapterUrlList = []
        self.myRequests = MyRequests()
        self.bookName = ""
        self.novelWebName = ""
        self.chapterNum = 0

    def login(self):
        print('novel web login')

    def search_book(self, key):
        resultList = []
        search_book_fun = [PiaoTianWenXue().search_book,
                           BaYiZhongWen().search_book,
                           Baidu().search_book,
                           # DingDian().search_book,
                           ]
        executor = ThreadPoolExecutor()

        # 开启搜索线程
        all_task = [executor.submit(search_book, key) for search_book in search_book_fun]

        # 等待返回结果
        for future in as_completed(all_task):
            yield future.result()
        #     resultList.append(future.result())
        # return resultList

    def parse_homeUrl(self, url):
        html, linkUrl = self.myRequests.get_html_and_linkUrl(url=url)
        # 通过链接的Url判断在哪个网站爬
        if self.webDomain_piaotian in linkUrl:
            print('飘天文学网')
            self.web_domain = self.webDomain_piaotian
            return PiaoTianWenXue().parse_homeUrl(linkUrl, html, self.web_domain)
        elif self.webDomain_bayi in linkUrl:
            print("八一中文网")
            self.web_domain = self.webDomain_bayi
            return BaYiZhongWen().parse_homeUrl(linkUrl, html, self.web_domain)
        # elif self.webDomain_dingdian in linkUrl:
        #     print("顶点小说")
        #     self.web_domain = self.webDomain_dingdian
        #     return DingDian().parse_homeUrl(linkUrl, html, self.web_domain)
        else:
            self.web_domain = ""
            return self.usual_parse_homeUrl(linkUrl, html)

    def parse_chapterHtml(self, html):
        if self.web_domain == self.webDomain_piaotian:
            return PiaoTianWenXue().parse_chapterHtml(html)
        elif self.web_domain == self.webDomain_bayi:
            return BaYiZhongWen().parse_chapterHtml(html)
        elif self.web_domain == self.webDomain_dingdian:
            return DingDian().parse_chapterHtml(html)
        else:
            return self.usual_parse_ChapterHtml(html)

    def save_book(self, bookName, chapterNameList, chapterContentList):
        if self.web_domain == self.webDomain_piaotian:
            PiaoTianWenXue().save_book(bookName, chapterNameList, chapterContentList)
        else:
            self.usual_save_book(bookName, chapterNameList, chapterContentList)

    def usual_parse_ChapterHtml(self, html):
        soup = BeautifulSoup(html, 'lxml')
        # temp
        try:
            # 找到小说章节内容
            temp = soup.find('div', id='content')
            if temp is None:
                temp = soup.find('div', attrs={'class': 'content'})
            temp = str(temp)

            # 去除小说章节内容中的非小说成分
            temp = re.sub('<br/><br/>', '\n', temp)
            temp = re.sub(r'c_t\(\);\s*', '', temp, 1)
            temp = re.sub(r'c_w\(\);.*$', '', temp)
            # temp = re.sub(r'mianhuatang.la \[棉花糖小说网\]', '', temp)
            # temp = re.sub(r'\[www.mianhuatang.la 超多好看小说\]', '', temp)
            # temp = re.sub(r'（wwW.mianhuatang.la 无弹窗广告）', '', temp)
        except:
            pass
        return BeautifulSoup(temp, "lxml").text  # 根据urls列表 排序章节内容顺序

    # 通常解析主页方法（可适用于 棉花糖小说网、新笔趣阁和部分笔趣阁）
    def usual_parse_homeUrl(self, linkUrl, html):
        try:
            soup = BeautifulSoup(html, 'lxml')
            print("linkUrl:" + linkUrl)
            # 获取小说书名
            # <meta name="og:novel:book_name" content="超神机械师" />
            meta = soup.find('meta', attrs={"name": "og:novel:book_name"})
            if meta is not None:
                self.bookName = meta['content']
            else:
                # <meta content = "超神机械师" property = "og:novel:book_name" />
                meta = soup.find('meta', attrs={"property": "og:novel:book_name"})
                if meta is not None:
                    self.bookName = meta['content']
    
            # 获取小说read_url
            # <meta property = "og:novel:read_url" content = "https://www.xbiquge6.com/77_77363/" />
            read_url = None
            meta = soup.find('meta', attrs={"property": "og:novel:read_url"})
            if meta is not None:
                read_url = meta['content']
            else:
                # <meta property = "og:url" content = "http://www.mianhuatang.la/63/63228/" />
                meta = soup.find('meta', attrs={"property": "og:url"})
                if meta is not None:
                    read_url = meta['content']

            print("bookname:" + str(self.bookName))
            print("read_url:" + str(read_url))

            # 获取小说网站 首页域名
            if "www.biquge.info" in read_url:
                self.web_domain = "www.biquge.info"

            print("web_domain:" + str(self.web_domain))

            adlist = soup.find('div', attrs={"class": "novel_list"})  # 找到章节列表

            # 如果未找到
            if adlist is None:
                adlist = soup.find('div', id='list')  # 找到章节列表
                if adlist is None:
                    adlist = soup.find('div', attrs={"class": "list"})  # 找到章节列表
                    adlist = adlist.find('dl')

            _as = adlist.find_all('a')
            for a in _as:
                href = a['href']
                chapterName = a.text
                self.chapterNameList.append(chapterName)
                self.chapterUrlList.append(href)

            # 获得base_url
            self.base_url = remove_duplicate_part_of_string(read_url, self.chapterUrlList[0])
            print("base_url:" + str(self.base_url))
            self.chapterNum = len(self.chapterNameList)
            return self.chapterNameList, self.chapterUrlList, self.base_url, self.bookName, self.web_domain, self.chapterNum
        except Exception as e:
            raise FError(repr(e))

    def usual_save_book(self, bookName, chapterNameList, chapterContentList):
        with open("%s.txt" % bookName, 'w', encoding='utf-8') as f:
            f.write("《%s》" % bookName + "\r\n\r\n\r\n")
            i = 0
            for chapterContent in chapterContentList:
                f.write(chapterNameList[i] + "\r\n\r\n\r\n" + chapterContent + "\r\n\r\n\r\n")
                i = i + 1
