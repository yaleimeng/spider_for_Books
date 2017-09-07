# -*- coding: utf-8 -*-
'''
@author: Yalei Meng    E-mail: yaleimeng@sina.com
@license: (C) Copyright 2017, HUST Corporation Limited.
@desc:
@DateTime: Created on 2017/9/6，at 13:14            '''
from bs4 import BeautifulSoup as bs
import requests as  rq
import time
import pymongo as mg
import  re
import random

client = mg.MongoClient('localhost',27017)
meng = client['meng']         #设定当前操作的数据库。=左边是python变量名，右边中括号里是MongoDB数据库名。
book_urls = meng['books']     #设定具体操作的数据表。=左边是python用的变量名，右边中括号里面是数据表名。
book_info = meng['book_info']


testP =  'http://category.dangdang.com/cp01.54.00.00.00.00.html'  #大的分类页面，用于测试get_books_from()函数。
#根据页码构造页码列表。可以作为get_books_from()的参数。
links = ['http://category.dangdang.com/pg{}-cp01.25.00.00.00.00.html'.format(str(i)) for i in range(1,101)]
def  get_books_from(listpage):
    r = rq.get(listpage)
    soup = bs(r.text, 'lxml')
    #books = soup.find('ul', class_='bigimg').find_all('a')  # 找到书的具体连接所在位置
    books = soup.select('ul.bigimg > li > a')
    for bk in books:
        print(bk['title'],bk['href'])
        book_urls.insert_one({'name':bk['title'],'link':bk['href']})


def get_book_info(bookpage):        #特殊情况需要判断是否为404找不到，这里不存在这个问题。所以省略。
    r = rq.get(bookpage)
    soup = bs(r.text, 'lxml')
    name = soup.find('div', class_='name_info').find('h1')['title']  # 找到书的名称所在位置
    info = soup.find('div',class_='messbox_info').find_all('span')
    author = info[0].text
    press = info[1].text
    pubdate = info[2].text
    descrip = soup.find('ul',class_='key clearfix').text
    bookid = bookpage.split('.')[-2].split('/')[1]          # 后面要用书id号构造js请求。
    price_url = 'http://product.dangdang.com/index.php?r=callback%2Fproduct-info&productId={}' \
                '&isCatalog=0&shopId=0&productType=0'.format(bookid)
    time.sleep(0.1)  # 比第1次页面请求推迟0.1秒
    res = rq.get(price_url)
    pj = res.json()
    newprice = pj['data']['spu']['price']['salePrice']
    oldprice = pj['data']['spu']['price']['originalPrice']

    list = soup.find_all('a',{ 'name':'__Breadcrumb_pub'})
    cate = list[-1]['href'].split('/')[-1][2:20]          #得到图书所在分类的字符串。构造JS请求获取评论数
    cateurl = 'http://product.dangdang.com/index.php?r=comment%2Flist&productId={}&categoryPath={}' \
              '&mainProductId={}&mediumId=0&pageIndex=1&sortType=1&filterType=1&isSystem=1&tagId=0&' \
              'tagFilterCount=0'.format(bookid,cate,bookid)
    time.sleep(0.1)          #比获取价格的JS请求再推迟0.1秒
    cRes =  rq.get(cateurl)
    cj = cRes.json()
    totalcmt = cj['data']['summary']['total_comment_num']   #得到评论总数
    goodRate = cj['data']['summary']['goodRate']            #得到好评率，不带%。

    bkdict = {'name':name, 'author':author[3:],'pubDate':pubdate[5:-1], 'Press':press[4:],
              'newPrice':newprice,  'oldPrice':oldprice,'totalComments':totalcmt,
              'goodRate':goodRate,'detail':descrip[1:],'link':bookpage}
    print(bkdict)
    # book_info.insert_one(dict)


#第一步，从构造好的链接列表中依次取出，抽取书的详情页的网址，保存到数据库。
# for  link in links:
#     get_books_from(link)
#     ra = random.uniform(2, 4)
#     print('休眠等待：%.3f秒'%ra)
#     time.sleep(ra)
# print('经济——门类全部收录完毕！')
#第二步，循环打开详情页，爬取图书的详细信息。在此仅用1个商品页面作为示例。
#发现收集到的图书链接有重复的，所以后面批量抓取时，必须进行去重。
get_book_info('http://product.dangdang.com/23274638.html')