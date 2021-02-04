# -*- coding: UTF-8 -*-
import __init__

from bs4 import UnicodeDammit

import requests
import time

from util.myUtil import FError


class MyRequests:
    headers = {
        'pragma': "no-cache",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.8",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'cache-control': "no-cache",
        'connection': "keep-alive",
    }
    def __init__(self, encode='utf-8'):
        self.encode = encode

    def get_html_and_linkUrl(self, url, webName="", header=None):  # 该函数速度较慢 适用于不知道某网页编码格式的情况
        try:
            t1 = time.time()
            if header == None:
                headers = self.headers
            else:
                headers = header
            r = requests.get(url, timeout=10, headers=headers)
            r.raise_for_status()
            # 自动选择合适的编码方式
            dammit = UnicodeDammit(r.content, ["utf-8", "gbk"])
            html = dammit.unicode_markup
            # print("%s requests 用时:" % webName + (round((time.time() - t1) * 1000)).__str__())
            return html, r.url
        except Exception as e:
            raise FError(repr(e))

    def get_html(self, url, webName=""):
        try:
            t1 = time.time()
            r = requests.get(url, timeout=10, headers=self.headers)
            r.raise_for_status()
            # 自动选择合适的编码方式
            dammit = UnicodeDammit(r.content, ["utf-8", "gbk"])
            html = dammit.unicode_markup
            # print("%s requests 用时:" % webName + (round((time.time() - t1) * 1000)).__str__())
            return html
        except Exception as e:
            raise FError(repr(e))
