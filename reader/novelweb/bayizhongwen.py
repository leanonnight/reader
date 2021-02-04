# -*- coding: UTF-8 -*-

import __init__
import time
from urllib import parse

from util.myUtil import remove_duplicate_part_of_string



from bs4 import BeautifulSoup

from util.myRequests import MyRequests



import requests
import re


class BaYiZhongWen(object):
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
        self.web_domain = "www.zwdu.com/"  # 小说网站主域名
        self.chapterNameList = []
        self.chapterUrlList = []
        self.bookName = ""
        self.novelWebName = ""
        self.chapterNum = 0


    def search_book(self, keyword):
        base_url = "https://www.zwdu.com/search.php"
        search = [('keyword', '%s' % keyword)]
        url = base_url + "?" + parse.urlencode(search, encoding='utf-8')  # 关键词转化为字符串
        html, linkUrl = MyRequests().get_html_and_linkUrl(url=url, webName='八一中文网')
        soup = BeautifulSoup(html, "lxml")
        divs = soup.findAll('div', class_="result-item result-game-item")
        times = 0
        for div in divs:
            try:
                captionDiv = div.find('div', class_="caption")
                title_a = div.find('a', cpos="title")
                self.title = title_a.text
                self.title = re.sub(r'\n', "", self.title)
                self.href = title_a['href']
                self.inline_block = div.find('p', class_='result-game-item-desc').text
                self.inline_block = re.sub('\u3000', "", self.inline_block)
                self.inline_block = re.sub(r'\n', " ", self.inline_block)
                self.theLasterChapter = div.find('a', cpos='newchapter').text
                self.coverImgUrl = div.find('a', cpos='img').img['src']
                item = {"title": self.title, "href": self.href, "inline_block": self.inline_block,
                        "theLasterChapter": self.theLasterChapter,
                        "coverImgUrl": self.coverImgUrl}
                self.resultList.append(item)
            except:
                pass
            times += 1
            if times == 3:   # 只获取最多前三个
                break
        return {'webName': "八一中文网", 'resultList': self.resultList}


    def parse_homeUrl(self, linkUrl, html = "", web_domain = ""):
        if html == "":
            html, linkUrl = MyRequests().get_html_and_linkUrl(url=linkUrl)
            self.web_domain = "www.zwdu.com"

        if web_domain is not "":
            self.web_domain = web_domain

        soup = BeautifulSoup(html, "lxml")
        info_div = soup.find('div', id='info')
        self.bookName = info_div.h1.text
        self.base_url = linkUrl

        div = soup.find('div', id="list")
        as_ = div.findAll('a')
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
        content = soup.find('div', id="content")
        content = str(content)
        content = re.sub('<br/>', "\r\n", content)
        return BeautifulSoup(content, 'lxml').text

    def save_book(self, bookName, chapterNameList, chapterContentList):
        pass

if __name__ == '__main__':
    web = BaYiZhongWen()
    print(web.search_book("超神"))
