import multiprocessing

import psutil
import requests
from bs4 import UnicodeDammit

header = {
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


headers1 = {
    "Referer": "http://www.mianhuatang520.com/search.aspx?bookname=%B3%AC%C9%F1%BB%FA%D0%B5%CA%A6",
    "Sec-Fetch-Mode": "no-cors",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

r = requests.post("http://www.mianhuatang520.com/ashx/zj.ashx", data={"action": "GetZj", "xsid": 42124}, headers=header)
print(r.text)

# str = "8291966%EF%BC%83%E9%82%BB%E5%AE%B6%E6%9C%89%E5%A5%B3%E5%88%9D%E9%95%BF%E6%88%90%EF%BD%9C8326575%EF%BC%83%E8%B6%85%E7%A5%9E%E6%9C%BA%E6%A2%B0%E5%B8%88%EF%BD%9C8329469%EF%BC%83%E7%89%A7%E7%A5%9E%E8%AE%B0"
#
# dammit = UnicodeDammit(str, ["utf-8", "gbk"])
# print(dammit.unicode_markup)