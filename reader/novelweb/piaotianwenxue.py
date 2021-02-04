# -*- coding: UTF-8 -*-

import __init__
import time
from urllib import parse

from bs4 import BeautifulSoup

from util.myRequests import MyRequests



import requests
import re


class PiaoTianWenXue(object):
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
        self.web_domain = "www.piaotian.org"  # 小说网站主域名
        self.chapterNameList = []
        self.chapterUrlList = []
        self.bookName = ""
        self.novelWebName = ""
        self.chapterNum = 0


    def search_book(self, keyword):
        base_url = "https://www.piaotian.org/modules/article/search.php"
        search = [('searchkey', '%s' % keyword)]
        url = base_url + "?" + parse.urlencode(search, encoding='gbk')  # 关键词转化为字符串
        html, linkUrl = MyRequests().get_html_and_linkUrl(url=url, webName='飘天文学网')
        soup = BeautifulSoup(html, "lxml")
        if "https://www.piaotian.org/modules/article/search.php?searchkey" in linkUrl:  # 多余一个搜索结果
            divs = soup.findAll('div', class_="col-md-4 col-xs-4 book-coverlist")
            times = 0
            for div in divs:
                try:
                    captionDiv = div.find('div', class_="caption")
                    self.title = captionDiv.h4.a['title']
                    self.href = captionDiv.h4.a['href']
                    self.inline_block = captionDiv.small.text
                    self.theLasterChapter = captionDiv.p.text
                    self.theLasterChapter = re.sub(r'\n\s*', " ", self.theLasterChapter)    # 去除换行符
                    self.coverImgUrl = div.find('img', class_="thumbnail")["src"]
                    item = {"title": self.title, "href": self.href, "inline_block": self.inline_block,
                            "theLasterChapter": self.theLasterChapter,
                            "coverImgUrl": self.coverImgUrl}
                    self.resultList.append(item)
                except:
                    pass
                times += 1
                if times == 3:   # 只获取最多前三个
                    break
        elif "https://www.piaotian.org/book/" in linkUrl:   # 得到精确的搜索结果
            try:
                self.title = soup.find('title').text
                self.href = linkUrl
                self.inline_block = soup.find('meta', property="og:novel:author")["content"]
                self.theLasterChapter = soup.find('meta', property="og:novel:latest_chapter_name")["content"]
                self.coverImgUrl = soup.find('img', class_="img-thumbnail")["src"]
                item = {"title": self.title, "href": self.href, "inline_block": self.inline_block,
                        "theLasterChapter": self.theLasterChapter,
                        "coverImgUrl": self.coverImgUrl}
                self.resultList.append(item)
            except:
                pass
        return {'webName': "飘天文学网", 'resultList': self.resultList}


    def parse_homeUrl(self, linkUrl, html = "", web_domain = ""):
        if html == "":
            html, linkUrl = MyRequests().get_html_and_linkUrl(url=linkUrl)
            self.web_domain = "www.piaotian.org"

        if web_domain is not "":
            self.web_domain = web_domain

        soup = BeautifulSoup(html, "lxml")
        panel_div = soup.find('div', attrs={"class": "panel-body"})
        bookTitle = panel_div.find('h1', class_="bookTitle").text
        self.bookName = re.sub(r'\s*/.*', "", bookTitle)
        self.base_url = linkUrl

        div = soup.find('div', id="list-chapterAll")
        as_ = div.findAll('a')
        for a in as_:
            try:
                self.chapterNameList.append(a['title'])
                self.chapterNameList.append("/2")
                self.chapterUrlList.append(a['href'])
                tempUrl = a['href'].split('.')
                self.chapterUrlList.append(tempUrl[0] + "_2.html")
            except:
                pass
        self.chapterNum = len(self.chapterNameList) / 2
        return self.chapterNameList, self.chapterUrlList, self.base_url, self.bookName, self.web_domain, self.chapterNum

    def parse_chapterHtml(self, html):
        soup = BeautifulSoup(html, 'lxml')
        contentDiv = soup.find('div', id="htmlContent")
        content = re.sub('飘天文学.*最新章节.', "", contentDiv.text, 1)
        content = re.sub('-->>本章未完，点击下一页继续阅读$', "", content, 1)
        return content

    def save_book(self, bookName, chapterNameList, chapterContentList):
        with open("%s.txt" % bookName, 'w', encoding='utf-8') as f:
            f.write("《%s》" % bookName + "  \r\n\r\n\r\n")
            index = 0
            for chapterContent in chapterContentList:
                if index % 2 == 0:
                    f.write(chapterNameList[index] + "  \r\n\r\n\r\n" + chapterContent)
                else:
                    f.write(chapterContent + "  \r\n\r\n\r\n")
                index += 1
#
# web = PiaoTianWenXue()
# print(web.search_book("超神"))
# #
# # # piaotianwenxue().parse_homeUrl("https://www.piaotian.org/book/8135/")
# html = MyRequests().get_html("https://www.piaotian.org/book/2223/1491726.html")
# print(PiaoTianWenXue().parse_chapterHtml(html))
# PiaoTianWenXue().parse_homeUrl("https://www.piaotian.org/book/2223/")
