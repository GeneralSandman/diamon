#! /usr/bin/env python
# coding=utf-8


import urllib2
import sys
import re
import json
from bs4 import BeautifulSoup

from basicCrawler import Crawler

'''
name
id
price
oldprice
shopname
GoodRateShow
newid

'''


class CrawlerJD(Crawler):
    # v2?callback

    #
    pass


header = {
    'referer': 'http://item.jd.com/12230538269.html',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537\
                        .36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
    'cookie': '__jdv=122270672|www.shenjianshou.cn|-|referral|-|1494932842923; ipLoc-djd=1-72-2799-0; __jda=122270672.1494932842919250345233.1494932843.1494932843.1494932843.1; __jdb=122270672.5.1494932842919250345233|1.1494932843; __jdc=122270672; 3AB9D23F7A4B3C9B=ZTFV5ON3CG2LCT'
              'EETWF5QWOEIPCDJAPHJZPVGDPDZCG4CPRCMPVJDK7V7VYJ5CQRW74HKMY5EFIBU7UYRPCCMZXYSY; __jdu=1494932842919250345233'
}


def getname():
    index_url = 'http://item.jd.com/12230538269.html'
    request = urllib2.Request(index_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    # print page
    soup = BeautifulSoup(page, 'html.parser')

    pa = r'<div class="item ellipsis" .*?>(.*?)</div>'
    pattern = re.compile(pa, re.S)
    name = soup.select('.sku-name')[0].text
    name = name.encode('utf-8').lstrip().rstrip()
    print name


def getPrice():
    price_url = 'http://p.3.cn/prices/mgets?callback=jQuery3778661&type=1&area=1_72_2799_0&pdtk=&pduid=1494932842919250345233&pdpin=&pdbp=0&skuIds=J_12230538269&source=item-pc'

    request = urllib2.Request(price_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read()
    jsondata = json.loads(page[15:-4])
    price = jsondata['p']
    oldprice = jsondata['op']
    print price
    print oldprice


def getseller():
    shop_url = 'http://chat1.jd.com/api/checkChat?&callback=jQuery7019280&pid=12230538269&returnCharset=utf-8&_=1495263921588'
    request = urllib2.Request(shop_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read()
    # print page[14:-2]
    jsondata = json.loads(page[14:-2])
    seller = jsondata['seller']
    shopId = jsondata['shopId']
    venderId = jsondata['venderId']
    print seller
    print shopId
    print venderId


def getComment():
    comment_url = 'http://club.jd.com/comment/productCommentSummaries.action?referenceIds=12230538269&callback=jQuery8150834&_=1495263921546'
    request = urllib2.Request(comment_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read()
    # print page[14:-2]
    jsondata = json.loads(page[14:-2])
    CommentsCount=jsondata['CommentsCount'][0]
    GoodRate=CommentsCount['GoodRate']
    GoodCount=CommentsCount['GoodCount']
    print GoodRate
    print GoodCount


def getRecommend():
    recommend_url = 'http://diviner.jd.com/diviner?lid=1&lim=6&ec=utf-8&uuid=1494932842919250345233&pin=&p=610008&sku=121932&ck=pin,ipLocation,atw,aview&c1=9987&c2=653&c3=655&callback=jQuery8852054&_=1495264859348'
    request = urllib2.Request(recommend_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read()
    # print page[14:-2]
    jsondata = json.loads(page[14:-2])
    for i in jsondata['data']:
        print i['sku']


def test():
    getname()
    getPrice()
    getseller()
    getComment()
    getRecommend()


if __name__ == "__main__":
    test()
