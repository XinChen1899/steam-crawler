# File: modifyData.py
# Date: 2021/11/13 10:29
# Author: ximu

import re
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup

#删除名称为空的行
def clear(path):
    df = pd.read_excel(path,index_col=0)
    df = df[~df['名称'].isin([' '])]
    df = df[~df['现价'].isin([' '])]
    df = df[~df['发行时间'].isin([' '])]
    df = df[~df['好评率'].isin([' '])]
    df = df.drop_duplicates()   #删除重复行
    df.to_excel(path)

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

def modify_now_price(df):
    try:
        pricenum = float(df['现价'].replace("¥ ", ""))
    except:
        pricenum = 0
    return pricenum

def modify_pre_price(df):
    try:
        pricenum = float(df['原价'].replace("¥ ", ""))
    except:
        pricenum = 0
    return pricenum

def modify_time(df):
    init = df['发行时间']
    try:
        year = re.findall(r'[0-9]{4}', init)[0]
        try:
            month = re.findall(r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec', init)[0]
            months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, "May": 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                      'Oct': 10, 'Nov': 11, 'Dec': 12}
            month_num = months[month]
            try:
                day = re.findall(r'[0-9]+', init)[0].replace(year, '')
                if day == '':
                    day = '1'
            except:
                day = '1'
        except:
            month_num = 1
            day = '1'
        return '%s-%d-%s' % (year, month_num, day)
    except:
        return ''

def modify_topseller_time(df):
    init = df['发行时间']
    try:
        year = re.findall(r'[0-9]{4}', init)[0]
        try:
            month = re.findall(r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec', init)[0]
            months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, "May": 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                      'Oct': 10, 'Nov': 11, 'Dec': 12}
            month_num = months[month]
        except:
            month_num = 1
        return '%s-%d' % (year, month_num)
    except:
        return ''

def modify_data(path):
    df = pd.read_excel(path, index_col=0)
    df['现价'] = df.apply(lambda x: modify_now_price(x), axis=1)
    df['现价'] = pd.to_numeric(df['现价'])  # 转为int64
    df['原价'] = df.apply(lambda x: modify_pre_price(x), axis=1)
    df['原价'] = pd.to_numeric(df['原价'])  # 转为int64
    df['发行时间'] = df.apply(lambda x: modify_time(x), axis=1)
    df.info()
    df.to_excel(path)

def modify_cate_topseller_data(path):
    df = pd.read_excel(path, index_col=0)
    df['现价'] = df.apply(lambda x: modify_now_price(x), axis=1)
    df['现价'] = pd.to_numeric(df['现价'])  # 转为int64
    df['发行时间'] = df.apply(lambda x: modify_topseller_time(x), axis=1)
    df.info()
    df.to_excel(path)

def modify_total_topseller_data(path):
    df = pd.read_excel(path, index_col=0)
    df['现价'] = df.apply(lambda x: modify_now_price(x), axis=1)
    df['现价'] = pd.to_numeric(df['现价'])  # 转为int64
    df['原价'] = df.apply(lambda x: modify_pre_price(x), axis=1)
    df['原价'] = pd.to_numeric(df['原价'])  # 转为int64
    df['发行时间'] = df.apply(lambda x: modify_topseller_time(x), axis=1)
    df.info()
    df.to_excel(path)

if __name__ == '__main__':
    path = 'init data'
    categories = get_catagories()
    announces = ['热销商品', '热门游戏', '最受好评']
    for category in categories:
        name = category['name']
        print(name)
        for announce in announces:
            print(announce)
            path1 = path + '/' + name + '/' + name + '_' + announce + 'info.xls'
            try:
                clear(path1)
                if announce == '热销商品':
                    modify_cate_topseller_data(path1)
                else:
                    modify_data(path1)
            except:
                print(name + ' 的 ' + announce + ' 有误')
    path2 = 'topseller data/热销商品_info.xls'
    try:
        clear(path2)
        modify_total_topseller_data(path2)
    except:
        print('总榜有误')
