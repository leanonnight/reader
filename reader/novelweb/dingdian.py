# -*- coding: UTF-8 -*-

import __init__
import time
import traceback
import re
from urllib import parse

from bs4 import BeautifulSoup

from util.myRequests import MyRequests


class DingDian:
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
        base_url = "https://www.x23us.com/modules/article/so.php"
        search = [('searchtype', 'keywords'), ('searchkey', '%s' % keyword)]
        url = base_url + "?" + parse.urlencode(search, encoding='gbk')  # 关键词转化为字符串
        html, linkUrl = MyRequests().get_html_and_linkUrl(url=url, webName='顶点小说')
        soup = BeautifulSoup(html, "lxml")
        if "https://www.x23us.com/modules/article/so.php?searchtype=keywords&searchkey" in linkUrl:  # 多余一个搜索结果
            tbody = soup.find('dl', id="content").tbody
            trs = soup.findAll('tr')
            times = -1
            for tr in trs:
                if times == -1:
                    times += 1
                    continue
                try:
                    # captionDiv = div.find('div', class_="caption")
                    tds = tr.findAll('td')
                    # print(tds[0])
                    self.title = tds[0].a.text
                    self.href = tds[1].a['href']
                    self.inline_block = tds[2].text
                    self.theLasterChapter = tds[1].text
                    self.coverImgUrl = ""
                    item = {"title": self.title, "href": self.href, "inline_block": self.inline_block,
                            "theLasterChapter": self.theLasterChapter,
                            "coverImgUrl": self.coverImgUrl}
                    self.resultList.append(item)
                except:
                    traceback.print_exc()
                times += 1
                if times == 3:   # 只获取最多前三个
                    break
        elif "https://www.x23us.com/book/" in linkUrl:   # 得到精确的搜索结果
            try:
                self.title = soup.find('dl', id='content').find('h1').text[:-5]
                self.href = soup.find('a', class_='read')['href']
                self.inline_block = soup.find('table', id='at').findAll('tr')[0].findAll('td')[1].text
                self.inline_block = re.sub('\xa0', "", self.inline_block)
                self.theLasterChapter = soup.find('dl', id='content').findAll('dd')[3].findAll('p')[5].a.text
                self.coverImgUrl = "https://www.x23us.com" + soup.find('a', class_='hst').img['src']
                item = {"title": self.title, "href": self.href, "inline_block": self.inline_block,
                        "theLasterChapter": self.theLasterChapter,
                        "coverImgUrl": self.coverImgUrl}
                self.resultList.append(item)
                # panel_div = soup.find('div', attrs={"class": "panel-body"})
            except:
                traceback.print_exc()
        return {'webName': "顶点小说", 'resultList': self.resultList}


    def parse_homeUrl(self, linkUrl, html = "", web_domain = ""):
        if html == "":
            html, linkUrl = MyRequests().get_html_and_linkUrl(url=linkUrl)
            self.web_domain = "www.x23us.com"

        if web_domain is not "":
            self.web_domain = web_domain

        soup = BeautifulSoup(html, "lxml")
        div = soup.find('div', class_="bdsub")
        self.bookName = div.dd.text[:-9]
        self.base_url = linkUrl

        table = soup.find('table', id="at")
        as_ = table.findAll('a')
        for a in as_:
            try:
                self.chapterNameList.append(a.text)
                self.chapterUrlList.append(a['href'])
            except:
                pass
        self.chapterNum = len(self.chapterNameList)
        return self.chapterNameList, self.chapterUrlList, self.base_url, self.bookName, self.web_domain, self.chapterNum

    def parse_chapterHtml(self, html):
        soup = BeautifulSoup(html, 'lxml')
        content_dd = soup.find('dd', id="contents")
        contents = str(content_dd)
        content = re.sub('<br/><br/>', "\r\n", contents)
        return BeautifulSoup(content, 'lxml').text

    def save_book(self, bookName, chapterNameList, chapterContentList):
        pass
        # with open("%s.txt" % bookName, 'w', encoding='utf-8') as f:
        #     f.write("《%s》" % bookName + "  \r\n\r\n\r\n")
        #     index = 0
        #     for chapterContent in chapterContentList:
        #         if index % 2 == 0:
        #             f.write(chapterNameList[index] + "  \r\n\r\n\r\n" + chapterContent)
        #         else:
        #             f.write(chapterContent + "  \r\n\r\n\r\n")
        #         index += 1

# DingDian().search_book("第一")
# print(DingDian().parse_homeUrl("https://www.x23us.com/html/73/73670/"))
# html = MyRequests().get_html("https://www.x23us.com/html/73/73670/33191125.html")
# print(DingDian().parse_chapterHtml(html))