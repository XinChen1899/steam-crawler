# File: countReviewWords.py
# Date: 2021/11/14 14:01
# Author: ximu
# Coding: UTF-8

import jieba
import jieba.posseg
import jieba.analyse
import re
import pandas as pd
from collections import Counter
import categoryInit

#获取停用词表
def get_stopwords():
    inf = open('stopwords.txt', encoding="UTF-8")
    line = inf.readline()
    list = []
    while line:
        line = line.replace('\n', '')
        list.append(line)
        line = inf.readline()
    return list

stopwords = get_stopwords()

#提取中文内容
def read_review(review):
    review = re.sub(r"[A-Za-z0-9\!\%\[\]\,\。\.|_|-|(|)|+|=|*|&|&|^|%|$|#|@|~|`|:|/|，|。|；|：|‘|“|、|”|’|？|！|·|（|）|【|】|{|}|——|—|《|》|<|>|-]", "", review)
    return review

#中文分词
def split_words(str1):
    str1 = read_review(str1)
    result = jieba.cut(str1, cut_all=False)
    outstr = ''
    # 去停用词
    for word in result:
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += " "
    result = jieba.cut(outstr, cut_all=False)
    return result

#词频统计
def count_words(x):
    str1 = x["评论"]
    seg_list = split_words(str1)
    c = Counter()
    for x in seg_list:
        if len(x) > 1 and x != '\r\n':
            c[x] += 1
    print(c)
    dic = dict(c)
    cwlist = []
    for key in dic:
        tup = (key, dic[key])
        cwlist.append(tup)
    return cwlist

def save_count_words(path):
    df = pd.read_excel(path, index_col=0)
    df['词频统计'] = df.apply(lambda x: count_words(x), axis=1)
    df.info()
    df.to_excel(path)

if __name__ == '__main__':
    path = 'init data'
    categories = categoryInit.get_catagories()
    announces = ['热门游戏', '最受好评']
    for category in categories:
        name = category['name']
        print(name)
        for announce in announces:
            print(announce)
            path1 = path + '/' + name + '/' + name + '_' + announce + 'info.xls'
            try:
                save_count_words(path1)
            except:
                print(name + ' 的 ' + announce + ' 有误')
