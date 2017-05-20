#! /usr/bin/env python
# coding=utf-8


import urllib2
import sys
import re
from bs4 import BeautifulSoup
import json
import redis
import pymongo
import ssl
import json


class Crawler(object):
    index_url_format = ''
    recommend_url_format = ''
    price_url_format = ''
    neighbor_url_format = ''
    header_referer = ''
    header = {
        'referer': header_referer,
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537\
                    .36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
        'cookie': 'thw=cn; uss=Vvj%2Fb%2FmcDDu3bLwb3%2FiUaIAaSHrBuYAD75abnbx%2B2lEznMNTHJKIRkYHsTU%3D; _cc_=URm48syIZQ%3D%3D; tg=0; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; uc3=sg2=UojdGMdD504k470pEENdBcjj1qGkgIha0WL%2FKHhX6ao%3D&nk2=&id2=&lg2=; tracknick=; _m_h5_tk=29cd69bb854c9424896b1fd747eac8a3_1492231771135; _m_h5_tk_enc=8df8d6b5e798603be654aaaf3fe95574; hng=CN%7Czh-CN%7CCNY; t=6573f87c43b6124d0cc883f011588c33; cookie2=1cdb31f173758802b2faf5948368d08e; v=0; l=AhwcqHEwuTf9MBYzzzkAAZzsbDDP18C/; isg=AhERTAKVLdaZf0FljACjuQeFIBSErIXwPTJAMPOnT1j3mjDsO8o0wIS6StmG; _tb_token_=77eb385e34a89; cna=ugPTEEBFswYCAcpu0bJJba8P; uc1=cookie14=UoW%2BuvlURrqCog%3D%3D; mt=ci%3D-1_0'
    }

    def __init__(self, id, redis_api, mongo_api):
        self.id = id
        self.redis_api = redis_api
        self.mongo_api = mongo_api
        self.index_url = self.index_url_format.format(Id=id)
        self.header['referer'] = self.index_url
        self.shopid = 0
        self.userid = 0
        self.name = ''
        self.shopname = ''
        self.descripe = ''
        self.soldCount = 0
        self.confirmGoodsCount = 0
        self.oldprice = 0
        self.price = 0
        self.newid = []

    def __init____(self):
        self.recommend_url = self.recommend_url_format.format(ShopId=self.shopid, Id=self.id, Page=1)
        self.price_url = self.price_url_format.format(Id=self.id, ShopId=self.shopid)
        self.neighbor_url = self.neighbor_url_format.format(Id=self.id, SellerId=self.userid)

    def Action(self):
        self.getInformation()
        self.printInformation()
        self.storeInformation()

    def getInformation(self):
        pass

    def printInformation(self):
        pass

    def storeInformation(self):
        pass


class CrawlerJD(Crawler):
    # v2?callback
    # checkChat?&callback.... ----seller,shopId,venderId
    # productCommentSummary
    # mgets?callback=j.... ----price
    # diviner?lid=1.... ----recommend
    #
    pass


def test():
    index_url = 'http://item.jd.com/12230538269.html'
    header = {
        'referer': index_url,
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537\
                        .36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
        'cookie': '__jdv=122270672|www.shenjianshou.cn|-|referral|-|1494932842923; ipLoc-djd=1-72-2799-0; __jda=122270672.1494932842919250345233.1494932843.1494932843.1494932843.1; __jdb=122270672.5.1494932842919250345233|1.1494932843; __jdc=122270672; 3AB9D23F7A4B3C9B=ZTFV5ON3CG2LCT'
                  'EETWF5QWOEIPCDJAPHJZPVGDPDZCG4CPRCMPVJDK7V7VYJ5CQRW74HKMY5EFIBU7UYRPCCMZXYSY; __jdu=1494932842919250345233'
    }
    request = urllib2.Request(index_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    page = page.encode("gbk")
    soup = BeautifulSoup(page, 'html.parser')

    print type(page)
    fd = open('index.txt', 'w')
    sys.stdout = fd
    print page
    fd.close()

    pa = r'<div class="item ellipsis" .*?>(.*?)</div>'
    pattern = re.compile(pa, re.S)
    name = soup.select('.item ellipsis')




if __name__ == "__main__":
    test()
