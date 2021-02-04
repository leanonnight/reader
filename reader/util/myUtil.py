# -*- coding: UTF-8 -*-

import __init__
import re

import time

#最简单的自定义异常
class FError(Exception):
    pass

# 去除字符串str1尾部和str2头部相同的部分
# 返回str1去除后的结果
def remove_duplicate_part_of_string(str1, str2):
    for i in range(0, len(str1)):
        for j in range(0, len(str2)):
            if str1[i] == str2[j]:
                # 如果str1尾部最后一个字符也相等 则说明str1头部和str2有相同的部分
                if i == len(str1) - 1:
                    return str1[0:len(str1) - j]
                i = i + 1
            else:
                break
        # 如果检索到str1最后一个字符也没找到相同部分 则返回str1
        if i == len(str1) - 1:
            return str1


########################################
# 改造章节名 改为能被小说软件识别的章节名
########################################
def reformChapterName(urlNum, chapterNameList):
    for i in range(urlNum):
        # 如果为标准章节名
        section1 = re.search(r'第.*章', chapterNameList[i])
        if section1 is not None:
            section1 = re.search(r'(第.*章)(.*)', chapterNameList[i])
            chapterNameList[i] = section1.group(1) + " " + section1.group(2)
            # print(section1.group())
            continue

        # 不标准文件名格式 如 001 xxx
        section = re.search(r'(\d*)(.*)', chapterNameList[i])
        if section is not None:
            section = section.groups()

            # 如果章节号为空 则此章节为作者题外话
            if section[0] == '':
                chapterNO = 0
            else:
                chapterNO = int(section[0])
                chapterNameList[i] = "第%d章 " % chapterNO + section[1]
    return chapterNameList

def test():
    print("test")
    pass