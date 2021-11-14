# File: categoryInit.py
# Date: 2021/11/1 11:13
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
    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)', 'Accept-Language': 'zh-CN'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36', 'Accept-Language': 'zh-CN'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50', 'Accept-Language': 'zh-CN'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0', 'Accept-Language': 'zh-CN'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0', 'Accept-Language': 'zh-CN'}
]

class steam_init(object):
    def __init__(self, link, announce):
        self.url = link
        self.headers = random.choice(headers)
        self.announce = announce
        #self.driver = webdriver.Chrome(executable_path='C:\Program Files\Google\Chrome\Application\chromedriver.exe')

    def get_page(self):
        response = requests.get(self.url, self.headers)
        str = '<span id="' +self.announce + "_total" +'">(.*?)</span>'
        com = re.compile(str)
        result = re.findall(com, response.text)[0]
        result = re.sub(r',','',result)
        max_page = int( int( result ) / 15 ) + 1
        if self.announce == 'TopSellers':
            if max_page < 1000:
                page_num = max_page
            else:
                page_num = 1000
        else:
            page_num = 2
        return int(page_num)

class steam_spider_request():
    def __init__(self, name, announce, page):
        self.headers = random.choice(headers)
        self.name = name
        self.announce = announce
        self.page = page

    def get_spider(self):
        srclist = []
        IDlist = []
        for page in tqdm(range(self.page)):
            #请求翻页链接
            url = 'https://store.steampowered.com/contenthub/querypaginated/tags/{0}/render/?query=&start={1}&count=15&cc=CN&l=schinese&v=4&tag={2}' \
                .format(self.announce, page * 15, self.name)
            html = requests.get(url, self.headers).text
            com = re.compile('https://store.steampowered.com/app/(.*?)/(.*?)/')
            com1 = re.compile('href="(.*?)"')
            result = re.sub(r'\\', '', html)
            result = re.findall(com1, result)
            '''
            *******************特殊处理*********************
            体育模拟:   %E4%BD%93%E8%82%B2%E6%A8%A1%E6%8B%9F
            在线竞技:   %E5%9C%A8%E7%BA%BF%E7%AB%9E%E6%8A%80
            恋爱:      %E6%81%8B%E7%88%B1
            局域网:    %E5%B1%80%E5%9F%9F%E7%BD%91
            **********************************************
            '''
            if len(result) == 0:
                #恋爱
                if self.name == '%E6%81%8B%E7%88%B1':
                    url = 'https://store.steampowered.com/contenthub/querypaginated/category/{0}/render/?query=&start={1}&count=15&cc=CN&l=schinese&v=4&tag=&category=sim_dating'\
                        .format(self.announce, page * 15)
                #体育模拟
                elif self.name == '%E4%BD%93%E8%82%B2%E6%A8%A1%E6%8B%9F':
                    url = 'https://store.steampowered.com/contenthub/querypaginated/category/{0}/render/?query=&start={1}&count=15&cc=CN&l=schinese&v=4&tag=&category=sports_sim'\
                        .format(self.announce, page * 15)
                #在线竞技
                elif self.name == '%E5%9C%A8%E7%BA%BF%E7%AB%9E%E6%8A%80':
                    url = 'https://store.steampowered.com/contenthub/querypaginated/category/{0}/render/?query=&start={1}&count=15&cc=CN&l=schinese&v=4&tag=&category=multiplayer_online_competitive'\
                        .format(self.announce, page * 15)
                #局域网
                else:
                    url = 'https://store.steampowered.com/contenthub/querypaginated/category/{0}/render/?query=&start={1}&count=15&cc=CN&l=schinese&v=4&tag=&category=multiplayer_lan'\
                        .format(self.announce, page * 15)
                html = requests.get(url, self.headers).text
                com = re.compile('https://store.steampowered.com/app/(.*?)/(.*?)/')
                com1 = re.compile('href="(.*?)"')
                result = re.sub(r'\\', '', html)
                result = re.findall(com1, result)
            for dat in result:
                srclist.append(str(dat))
                IDlist.append(re.findall(com, str(dat))[0][0])
            #print('已完成{}页的内容'.format(page))
        return srclist,IDlist

    def save(self):
        srclist, IDlist= self.get_spider()
        df = pd.DataFrame(list(zip(srclist, IDlist)),
                          columns=['链接', 'ID'])
        return df

def get_catagories():
    unique_tags = ['免费游玩', '试玩', '抢先体验', '支持控制器', '远程畅玩', '软件', '原声音轨', '虚拟现实', 'VR 硬件', 'Steam Deck', 'macOS',
                   'SteamOS + Linux', '网吧游戏']
    url = 'https://store.steampowered.com'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
              'Accept-Language': 'zh-CN'}
    req = urllib.request.Request(url=url, headers=header)
    # 打开页面
    webpage = urllib.request.urlopen(req)
    # 读取页面内容
    html = webpage.read()
    # 解析成文档对象66
    soup1 = BeautifulSoup(html, 'html.parser')
    j = soup1.find_all('div', attrs='popup_block_new flyout_tab_flyout responsive_slidedown', id='genre_flyout')
    soup2 = BeautifulSoup(str(j), 'html.parser')
    list = []
    for k in soup2.find_all('a', attrs='popup_menu_item'):
        dict = {}
        link = k.get('href')
        if len(k.contents) > 1:
            name = k.contents[1].contents[0].lstrip()
        else:
            name = k.contents[0].lstrip().rstrip()
        if name not in unique_tags:
            dict['name'] = name
            dict['link'] = link
            list.append(dict)
    return list



if __name__ == '__main__':
    path = 'init data'
    if not os.path.exists(path):
        os.makedirs(path)
    announces = ['热销商品', '热门游戏', '最受好评']
    announce = ''
    catagories = get_catagories()
    print(catagories)
    num = ['TopSellers','ConcurrentUsers','TopRated']
    for catagory in catagories:
        name = catagory['name']
        print(name)
        try:
            for i in range(0,3):
                annouce = announces[i]
                print(annouce)
                game_type = name
                game_type = urllib.parse.quote(game_type)
                game_anno = i
                #获取最大页数，返回想要爬取的页数0
                steam = steam_init(catagory['link'], num[game_anno])
                page = steam.get_page()
                spider = steam_spider_request(game_type, num[game_anno], page)
                # spider.get_spider(page)
                save = spider.save()
                path1 = path + '/' + name
                if not os.path.exists(path1):
                    os.makedirs(path1)
                path2 = path1 + '/' + name + '_' + annouce + 'links.xls'
                file = open(path2, 'wb')
                file.close()
                save.to_excel(path2)
        except:
            print(name + " 有误!!")


