# -*- coding: UTF-8 -*-

import __init__
import time
from urllib import parse

from util.myUtil import remove_duplicate_part_of_string



from bs4 import BeautifulSoup

from util.myRequests import MyRequests



import requests
import re


class BiQuGe(object):
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
        self.web_domain = "www.bequgew.com/"  # 小说网站主域名
        self.chapterNameList = []
        self.chapterUrlList = []
        self.bookName = ""
        self.novelWebName = ""
        self.chapterNum = 0


    def search_book(self, keyword):
        base_url = "http://www.bequgew.com/modules/article/search.php"
        search = [('searchkey', '%s' % keyword)]
        url = base_url + "?" + parse.urlencode(search, encoding='utf-8')  # 关键词转化为字符串
        html, linkUrl = MyRequests().get_html_and_linkUrl(url=url, webName='笔趣阁')
        soup = BeautifulSoup(html, "lxml")
        table = soup.find('table', class_="grid")

        trs = table.findAll('tr')
        times = -1
        for tr in trs:
            if times == -1:
                times += 1
                continue
            try:
                tds = tr.findAll('td')
                self.title = tds[0].text
                self.href = tds[0].a['href']
                self.inline_block = "作者:" + tds[2].text + " 大小:" + tds[3].text + " 最后更新:" + tds[4].text
                self.theLasterChapter = tds[1].text
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
        return {'webName': "笔趣阁", 'resultList': self.resultList}


    def parse_homeUrl(self, linkUrl, html = "", web_domain = ""):
        if html == "":
            html, linkUrl = MyRequests().get_html_and_linkUrl(url=linkUrl)
            self.web_domain = "www.bequgew.com"

        if web_domain is not "":
            self.web_domain = web_domain

        soup = BeautifulSoup(html, "lxml")
        div = soup.find('div', class_='info')
        self.bookName = div.h1.text
        self.base_url = linkUrl

        div = soup.find('div', class_="article_texttitleb")
        lis = div.findAll('li')
        for li in lis:
            a = li.a
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
        content = soup.find('div', id="book_text")
        content = str(content)
        content = re.sub('<br/>', "\r\n", content)
        return BeautifulSoup(content, 'lxml').text

    def save_book(self, bookName, chapterNameList, chapterContentList):
        pass

if __name__ == '__main__':
    web = BiQuGe()
    for x in web.search_book("超神")['resultList']:
        print(x)

    # x, y, j, k, w, l = web.parse_homeUrl("http://www.bequgew.com/112864/")
    #
    # print(l)
    # for i in range(l):
    #     print(str(i) + ":" + x[i] + "  " + y[i])

    # html, linkUrl = MyRequests().get_html_and_linkUrl(url="http://www.bequgew.com/112864/37447449.html")
    # print(web.parse_chapterHtml(html))