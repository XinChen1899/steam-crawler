# File: TopSellerInfo.py
# Date: 2021/11/12 23:41
# Author: ximu

import categoryInit
from lxml import etree
import random
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = [
    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'}
]

count = 0

def get_type(html):
    str = ' '
    final_cost = html.xpath('//div[@class="glance_tags popular_tags"]/a')
    for i in final_cost[0:6]:   #输出前6个标签
        str = str + i.text + ', '
    return str

def clear(str):
    com = re.sub(r'\t|\r\n','',str)
    return com

def get_normal_detail(x):
    #名称     原价   现价  标签   近评   全评    好评率    评价人数    游戏描述   游戏类型   发布时间    开发商
    game_name, original_cost ,final_cost, tags, now_evaluate, all_evaluate, rate, people, des, type, time, deve =' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',' ',' '
    header = random.choice(headers)
    global count
    try:
        html = requests.get(x['链接'], headers = header, timeout=10).text
        xml = etree.HTML(html)
    except:
        print('服务器1没响应，正在重新请求')
        try:
            html = requests.get(x['链接'], headers = header, timeout=10).text
            xml = etree.HTML(html)
        except:
            print('服务器2没响应，正在重新请求')
            try:
                html = requests.get(x['链接'], headers=header, timeout=10).text
                xml = etree.HTML(html)
            except:
                print('服务器没响应,直接进入下一个')
                #html = requests.get(x['链接'], headers=header, timeout=10).text
    try:
        game_name = xml.xpath('//div[@class="apphub_AppName"]')[0].text
        try:
            original_cost = xml.xpath('//div[@class="discount_prices"]/div[1]')[0].text
            final_cost = xml.xpath('//div[@class="discount_prices"]/div[2]')[0].text
        except:
            original_cost = xml.xpath('//div[@class="game_purchase_price price"]')[0].text
            original_cost = clear(original_cost)
            final_cost = xml.xpath('//div[@class="game_purchase_price price"]')[0].text
            final_cost = clear(final_cost)
        try:
            now_evaluate = xml.xpath('//div[@class="summary column"]/span[1]')[0].text
            all_evaluate = xml.xpath('//div[@class="summary column"]/span[1]')[1].text
            rate = re.match('[0-9]+%', xml.xpath('//div[@class="user_reviews_summary_row"]/@data-tooltip-html')[0]).group()
            people = clear(xml.xpath('//div[@class="summary column"]/span[2]')[0].text)[1:-1]
        except:
            now_evaluate = "None"
            all_evaluate = xml.xpath('//div[@class="summary column"]/span[1]')[0].text
            rate = re.match('[0-9]+%', xml.xpath('//div[@class="user_reviews_summary_row"]/@data-tooltip-html')[0]).group()
            people = clear(xml.xpath('//div[@class="summary column"]/span[2]')[0].text)[1:-1]

        tags = get_type(xml)
        des = clear(xml.xpath('//div[@class="game_description_snippet"]')[0].text)
        type = get_type(xml)
        time = xml.xpath('//div[@class="date"]')[0].text
        deve = xml.xpath('//div[@class="dev_row"]/div[2]/a[1]')[0].text
    except:
        print('第{}个游戏未完成检索'.format(count))

    count += 1
    return game_name, original_cost, final_cost, tags, now_evaluate, all_evaluate, rate, people, des, type, time, deve

def normal_info(in_path, out_path):
    df = pd.read_excel(in_path)

    df['详细']     = df.apply(lambda x: get_normal_detail(x), axis=1)
    df['名称']     = df.apply(lambda x:x['详细'][0], axis=1)
    df['原价']     = df.apply(lambda x:x['详细'][1], axis=1)
    df['现价']     = df.apply(lambda x:x['详细'][2], axis=1)
    df['标签']     = df.apply(lambda x:x['详细'][3], axis=1)
    df['最近评价']  = df.apply(lambda x:x['详细'][4], axis=1)
    df['全部评价']  = df.apply(lambda x:x['详细'][5], axis=1)
    df['好评率']   = df.apply(lambda x:x['详细'][6], axis=1)
    df['评价人数']  = df.apply(lambda x:x['详细'][7], axis=1)
    df['游戏描述']  = df.apply(lambda x:x['详细'][8], axis=1)
    df['类型']      = df.apply(lambda x:x['详细'][9], axis=1)
    df['发行时间']  = df.apply(lambda x:x['详细'][10], axis=1)
    df['开发商']   = df.apply(lambda x:x['详细'][11], axis=1)

    df = df.drop('Unnamed: 0', axis=1)   #删掉没用的数据
    df.to_excel(out_path)
    df.info()
    print('---检索完成---')

if __name__ == '__main__':
    path = 'topseller data'
    try:
        in_path = path + '/' + '热销商品_links.xls'
        out_path = path + '/' + '热销商品_info.xls'
        normal_info(in_path, out_path)
    except:
        print("Error")
