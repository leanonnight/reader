# -*- coding: UTF-8 -*-

import __init__

import re
import traceback

from util.myUtil import test
from util.myUtil import FError
from util.myRequests import MyRequests
from urllib import parse
from bs4 import BeautifulSoup
import time
from lxml import etree


class Baidu:
    def __init__(self):
        self.resultList = []

    def search_book(self, keyword):
        try:
            base_url = "http://www.baidu.com/s"
            search = [('wd', '%s' % keyword)]
            url = base_url + "?" + parse.urlencode(search)  # 关键词转化为字符串
            html = MyRequests("utf-8").get_html(url=url, webName='百度')
            soup = BeautifulSoup(html, "lxml")
            divs = soup.find_all("div", attrs={"class": 'result c-container'})
            title = ""
            href = ""
            inline_block = ""
            theLasterChapter = ""
            coverImgUrl = ""     # 封面
            times = 0
            for div in divs:
                try:
                    # 去除 table标签中的html格式空格
                    div = re.sub('\xa0', '', str(div))
                    div = BeautifulSoup(div, 'lxml')
                    title = div.h3.text
                    href = div.h3.a['href']
                    inline_block = div.div.span.text
                    theLasterChapter = div.find('p', attrs={'class': "c-gray"}).text
                    # coverImgUrl = div.find('img')['src']
                    # print("baidu 用时:" + (round((time.time() - self.t1) * 1000)).__str__())
                except BaseException as e:
                    pass
                item = {"title": title, "href": href, "inline_block": inline_block, "theLasterChapter": theLasterChapter, "coverImgUrl": coverImgUrl}
                self.resultList.append(item)
                times += 1
                if times == 3:  # 只获取最多前三个
                    break
            return {'webName': "百度", 'resultList': self.resultList}
        except Exception as e:
            # raise FError(repr(e))
            pass


if __name__ == '__main__':
    x = Baidu().search_book("第一序列")
    for y in x:
        print(x)
