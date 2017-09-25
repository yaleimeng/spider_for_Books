# -*- coding: utf-8 -*-
'''
@author: Yalei Meng    E-mail: yaleimeng@sina.com
@license: (C) Copyright 2017, HUST Corporation Limited.
@DateTime: Created on 2017/9/23，at 15:57            '''
from bs4 import BeautifulSoup as bs
import requests as rq
import time
import re

def request_Page(page , refer = ''):    #对页面请求并按utf-8解码
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0'
    head = {'User-Agent': ua ,'Referer':refer}
    r = rq.get(page, headers=head, timeout=5)
    r.encoding = 'urf-8'
    return r

def getBookUrls(Page):
    soup = bs(request_Page(Page).text,'lxml')
    books = soup.select('li.gl-item div.p-img a')
    thirty = ''
    for bk in books:
        link = 'http:'+bk['href']
        print(bk['title'], link)
        if link not in bkurls:
            bkurls.append(link)
        thirty += bk['href'].split('/')[-1].split('.')[0]
        thirty += ','
    argu = thirty[:-1]
    rgxp = re.compile('log_id.*\d+\.\d+')
    logid = rgxp.search(text).group().split("'")[-1]
    num = int(Page.split('&')[-3].split('=')[1])
    jsurl = 'https://search.jd.com/s_new.php?keyword=Python&enc=utf-8&qrst=1&rt=1&stop=1&book=y&vt=2&cid2=3287&stock=1' \
            '&page={}&s={}&scrolling=y&log_id={}&tpl=2_M&show_items={}'.format(str(num+1),str(num*30+1),logid,argu)
    time.sleep(0.35)
    soup = bs(request_Page(jsurl,Page).text,'lxml')
    books = soup.select('li.gl-item div.p-img a')
    for bk in books:
        link = 'http:'+bk['href']
        print(bk['title'],link)
        if link not in bkurls:
            bkurls.append(link)

if __name__ == '__main__':        #可以设置自己关键词的搜索URL入口
    start = ['https://search.jd.com/search?keyword=Python&enc=utf-8&qrst=1&rt=1&stop=1&book=y'
             '&vt=2&cid2=3287&stock=1&page={}&s={}&click=0'.format(str(i*2-1),str((i-1)*60+1))
             for i in range(1,101)    ]

    bkurls = []
    for art in start:
        getBookUrls(art)
        time.sleep(0.6)
    print('运行完毕，得到书的链接数量：',len(bkurls))
    with open('E:/JD_urls.txt', 'a', encoding='utf-8')as f:
        for bk in bkurls:
            f.write(bk)
            f.write("\n")
    print('所有URL写入txt文件完毕！')