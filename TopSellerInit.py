# File: TopSellerInit.py
# Date: 2021/11/12 23:14
# Author: ximu

import os
import requests
import urllib
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import re
import random
import pandas as pd
from tqdm import tqdm

headers = [
    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'}
]

class steam_topseller_spider_request():
    def __init__(self, page):
        self.headers = random.choice(headers)
        self.page = page

    def get_spider(self):
        srclist = []
        for page in tqdm(range(self.page)):
            #请求翻页链接
            url = 'https://store.steampowered.com/search/results/?query&start={0}&count=50&dynamic_data=&sort_by=_ASC&snr=1_7_7_globaltopsellers_7&filter=globaltopsellers&os=win&infinite=1' \
                .format(page * 50)
            html = requests.get(url, self.headers).text
            #com = re.compile('https://store.steampowered.com/app/(.*?)/(.*?)/')
            com1 = re.compile('href="(.*?)"')
            result = re.sub(r'\\', '', html)
            result = re.findall(com1, result)
            for dat in result:
                srclist.append(str(dat))
            #print('已完成{}页的内容'.format(page))
        return srclist

    def save(self):
        srclist= self.get_spider()
        df = pd.DataFrame(list(zip(srclist)),
                          columns=['链接'])
        return df

if __name__ =='__main__':
    path = 'topseller data'
    if not os.path.exists(path):
        os.makedirs(path)
    spider = steam_topseller_spider_request(600)
    # spider.get_spider(page)
    save = spider.save()
    path1 = path + '/' + '热销商品_links.xls'
    file = open(path1, 'wb')
    file.close()
    save.to_excel(path1)
