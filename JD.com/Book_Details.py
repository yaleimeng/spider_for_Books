# -*- coding: utf-8 -*-
'''
@author: Yalei Meng    E-mail: yaleimeng@sina.com
@license: (C) Copyright 2017, HUST Corporation Limited.
@DateTime: Created on 2017/9/23，at 17:38            '''
from bs4 import BeautifulSoup as bs
import requests as rq
import time
import random
import json
import pymongo as mg
from BookURL import request_Page

def get_Detail_from(book_page):
    soup = bs(request_Page(book_page).content,'lxml')
    name = '' if  len(soup.select('div#name h1')) == 0 else  soup.select('div#name h1')[0].text.replace(' ','')
    author = '' if  len(soup.select('div#p-author')) == 0 else soup.select('div#p-author')[0].text.replace('\n','').replace(' ','')
    if name =='' and author =='':  #如果没有书名和作者，那么不需要再继续。
        return
    detail = soup.select('ul.p-parameter-list')[0].text[1:-1].replace(' ','')
    shop = '京东' if soup.select('ul.p-parameter-list li')[0].text[:3] == '出版社' \
        else  soup.select('ul.p-parameter-list li')[0]['title']
    id = book_page.split('/')[-1].split('.')[0]

    jsurl = 'https://p.3.cn/prices/get?type=1&area=1_72_2799&ext=11000000&pin=&pdtk=&pduid=1506124005948838590885&' \
            'pdtk={}&pdpin=&pdbp=0&skuid=J_{}&callback=cnp'.format('token',id)
    time.sleep(0.07)
    str  = request_Page(jsurl).text[5:-4]
    print(str)
    info = json.loads(str)
    old_price = float(info['m']);    norm_pri = float( info['op']);    new_price = float(info['p'])

    cmturl = 'http://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'.format(id)
    time.sleep(0.07)
    str = request_Page(cmturl).text
    info = json.loads(str)
    total = int(info['CommentsCount'][0]['CommentCount']);    good_rate = float(info['CommentsCount'][0]['GoodRate'])
    dict = { '书名':name,   '作者':author,   '店铺': shop,       '现价': new_price,  '定价': old_price,
        '日常价': norm_pri, '评论数': total, '好评率':good_rate, '详情': detail,     '链接': book_page    }
    print(dict)
    pyBook.insert_one(dict)

#单个URL测试函数效果。
# test = 'http://item.jd.com/11322663.html'
# get_Detail_from(test)

if __name__ == '__main__':         #批量采集数据。
    urls,data = [],[]
    with open('E:/JD_urls.txt', 'r', encoding='utf-8')as f:
        for line in f.readlines():         # 按整行依次读取数据。
            link = line.replace("\n", '')  # 把回车符号替换为空。这样网址就是可访问的。
            urls.append(link)

    client = mg.MongoClient('localhost',27017)
    JD = client['JingDong']      #设定要操作的数据库。=左边是python变量名，右边中括号里是MongoDB数据库名。
    pyBook = JD['pythonBook']    #设定要操作的数据表。=左边是python用的变量名，右边中括号里面是数据表名。

    up,down = 1, 6000
    for n in range(up,down):
        get_Detail_from(urls[n])
        print('数据库条目总数：', pyBook.count())
        time.sleep(random.uniform(0.4,1.2))

    print('恭喜！\n程序运行完毕，数据库中条目总数：', pyBook.count())
