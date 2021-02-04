# -*- coding: UTF-8 -*-

import __init__
import time
from urllib import parse

from util.myUtil import remove_duplicate_part_of_string



from bs4 import BeautifulSoup

from util.myRequests import MyRequests


import traceback
import requests
import re


class MianHuaTang(object):
    # 请求头
    request_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "cuid=www.mianhuatang520.com_2020-2-18_15:40:31:264_74; UM_distinctid=170573dc8559c-076965c6a710f7-67e1b3f-1fa400-170573dc85670d; bgcolor=#f6f6f6; fontcolor=#000000; fontsize=16px; fontfamily=%E5%AE%8B%E4%BD%93; divwidth=80%25; ASP.NET_SessionId=gcshn0f2yneevozii0dyfysx; CNZZDATA1278595178=943833220-1582010537-null%7C1583572818; CNZZDATA1255974359=331824195-1582006428-https%253A%252F%252Fwww.baidu.com%252F%7C1583575708; userbook=8138000%EF%BC%83%E8%BF%9B%E5%8C%96%E7%9A%84%E5%9B%9B%E5%8D%81%E5%85%AD%E4%BA%BF%E9%87%8D%E5%A5%8F%EF%BD%9C8114917%EF%BC%83%E5%A4%A7%E6%98%8E%E5%B4%87%E7%A5%AF%E6%96%B0%E4%BC%A0%EF%BD%9C8291966%EF%BC%83%E9%82%BB%E5%AE%B6%E6%9C%89%E5%A5%B3%E5%88%9D%E9%95%BF%E6%88%90%EF%BD%9C8326575%EF%BC%83%E8%B6%85%E7%A5%9E%E6%9C%BA%E6%A2%B0%E5%B8%88%EF%BD%9C8329469%EF%BC%83%E7%89%A7%E7%A5%9E%E8%AE%B0; LookNum=5",
        "Host": "www.mianhuatang520.com",
        "If-Modified-Since": "Sat, 07 Mar 2020 10:39:32 GMT",
        "Referer": "http://www.mianhuatang520.com/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    }
    web_domain = "www.mianhuatang520.com"  # 小说网站主域名
    webName = "棉花糖"
    def __init__(self):
        # 搜书
        self.title = ""
        self.href = ""
        self.inline_block = ""
        self.theLasterChapter = ""
        self.coverImgUrl = ""  # 封面
        self.resultList = []

        # 解析网页
        self.base_url = ""  # 小说主页基url
        self.chapterNameList = []
        self.chapterUrlList = []
        self.bookName = ""
        self.novelWebName = ""
        self.chapterNum = 0


    def search_book(self, keyword):
        base_url = "http://www.mianhuatang520.com/search.aspx"
        search = [('bookname', '%s' % keyword)]
        url = base_url + "?" + parse.urlencode(search, encoding='gbk')  # 关键词转化为字符串
        html, linkUrl = MyRequests().get_html_and_linkUrl(url=url, webName=self.webName, header=self.request_headers)
        soup = BeautifulSoup(html, "lxml")
        table = soup.find('div', id="newscontent")
        items = table.findAll('li')

        times = 0
        for item in items:
            if times == -1:
                times += 1
                continue
            try:
                spans = item.findAll('span')
                self.title = spans[1].text
                self.title = re.sub(r'\n*', "", self.title)  # 去除换行符
                self.href = spans[1].a['href']
                self.inline_block = "作者:" + spans[3].text + " 最后更新:" + spans[4].text
                self.theLasterChapter = spans[2].text
                self.coverImgUrl = "None"
                item = {"title": self.title, "href": self.href, "inline_block": self.inline_block,
                        "theLasterChapter": self.theLasterChapter,
                        "coverImgUrl": self.coverImgUrl}
                self.resultList.append(item)
            except:
                pass
            times += 1
            if times == 3:   # 只获取最多前三个
                break
        return {'webName': self.webName, 'resultList': self.resultList}


    def parse_homeUrl(self, linkUrl, html = "", web_domain = ""):
        if html == "":
            bookid_str = re.findall(r"http://www.mianhuatang520.com/xs/(\d+)/", linkUrl)[0]
            bookid = int(bookid_str) - 8111811
        if web_domain is not "":
            self.web_domain = web_domain
        response = requests.post("http://www.mianhuatang520.com/ashx/zj.ashx", data={"action": "GetZj", "xsid": bookid}, headers=self.request_headers)
        soup = BeautifulSoup(response.text, "lxml")
        as_ = soup.findAll('a')
        for a in as_:
            try:
                self.chapterNameList.append(a.text)
                self.chapterUrlList.append(a['href'])
            except:
                pass

        # 改造base_url
        self.base_url = remove_duplicate_part_of_string(linkUrl, self.chapterUrlList[0])
        print("base_url:" + str(self.base_url))

        self.chapterNum = len(self.chapterNameList)
        return self.chapterNameList, self.chapterUrlList, self.base_url, self.bookName, self.web_domain, self.chapterNum

    def parse_chapterHtml(self, html):
        soup = BeautifulSoup(html, 'lxml')
        content = soup.find('div', id="zjneirong")
        content = str(content)
        content = re.sub('<br/>', "\r\n", content)
        return BeautifulSoup(content, 'lxml').text[:-144]

    def save_book(self, bookName, chapterNameList, chapterContentList):
        pass

if __name__ == '__main__':
    web = MianHuaTang()

    ################
    #   搜索
    ################
    # print(web.search_book("超神"))
    # for x in web.search_book("超神")['resultList']:
    #     print(x)

    ################
    #   解析主页
    ################
    # x, y, j, k, w, l = web.parse_homeUrl("http://www.mianhuatang520.com/xs/8116272/")
    #
    # print(l)
    # for i in range(l):
    #     print(str(i) + ":" + x[i] + "  " + y[i])

    ######################
    #   解析章节内容
    ######################
    html, linkUrl = MyRequests().get_html_and_linkUrl(url="http://www.mianhuatang520.com/xs/8116272/81260331.htm")
    print(web.parse_chapterHtml(html))