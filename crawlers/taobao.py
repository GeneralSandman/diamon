#! /usr/bin/env python
# coding=utf-8



import urllib2
import re
from bs4 import BeautifulSoup
import ssl
import json

import api.mongodb
import api.redis

json_data = {}




class CrawlerTaobao(object):
    index_url_format = 'https://item.taobao.com/item.htm?id={Id}'
    recommend_url_format = 'https://tui.taobao.com/recommend?sellerid={ShopId}&categoryid=50000671&itemid={Id}&callback=detail_pine&appid=4935&count=6&page={Page}'
    price_url_format = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={Id}&sellerId={ShopId}&modules=dynStock,qrcode,viewer,price,contract,duty,xmpPromotion,delivery,upp,activity,fqg,zjys,amountRestriction,couponActivity,soldQuantity&callback=onSibRequestSuccess'
    neighbor_url_format = 'https://tui.taobao.com/recommend?itemid={Id}&sellerid={SellerId}&_ksTS=1492592500496_0000&callback=jsonp1800&appid=3066'
    header = {
        'referer': 'https://item.taobao.com/item.htm?id={Id}',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537\
                    .36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
        'cookie': 'thw=cn; uss=Vvj%2Fb%2FmcDDu3bLwb3%2FiUaIAaSHrBuYAD75abnbx%2B2lEznMNTHJKIRkYHsTU%3D; _cc_=URm48syIZQ%3D%3D; tg=0; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; uc3=sg2=UojdGMdD504k470pEENdBcjj1qGkgIha0WL%2FKHhX6ao%3D&nk2=&id2=&lg2=; tracknick=; _m_h5_tk=29cd69bb854c9424896b1fd747eac8a3_1492231771135; _m_h5_tk_enc=8df8d6b5e798603be654aaaf3fe95574; hng=CN%7Czh-CN%7CCNY; t=6573f87c43b6124d0cc883f011588c33; cookie2=1cdb31f173758802b2faf5948368d08e; v=0; l=AhwcqHEwuTf9MBYzzzkAAZzsbDDP18C/; isg=AhERTAKVLdaZf0FljACjuQeFIBSErIXwPTJAMPOnT1j3mjDsO8o0wIS6StmG; _tb_token_=77eb385e34a89; cna=ugPTEEBFswYCAcpu0bJJba8P; uc1=cookie14=UoW%2BuvlURrqCog%3D%3D; mt=ci%3D-1_0'
    }
    recommend_url = ''

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
        self.getInfo()
        self.getPrice()
        self.getMoreId()

    def printInformation(self):
        print'Id:', self.id, type(self.id)
        print'商品名称:', self.name, type(self.name)
        print'店铺名称:', self.shopname, type(self.shopname)
        print'商品描述:', self.descripe, type(self.descripe)
        print'销量:', self.soldCount, type(self.soldCount)
        print'交易成功:', self.confirmGoodsCount, type(self.confirmGoodsCount)
        print'原价:', self.oldprice, type(self.oldprice)
        print'现价:', self.price, type(self.price)
        print'Newid:', len(self.newid), self.newid, type(self.newid[0])

    def storeInformation(self):
        self.mongo_api.add({'商品ID': self.id, '商品名称': self.name, '价格': self.price, '商品描述': self.descripe, \
                            '月销量': int(self.soldCount), '交易成功': self.confirmGoodsCount, '原价': int(self.oldprice),
                            '店铺': self.shopname})
        global json_data
        json_data['Id'] = self.id
        json_data['Name'] = self.name
        json_data['Price'] = self.price
        json_data['Descripe'] = self.descripe
        json_data['SoldCount'] = self.soldCount
        json_data['ConfirmGoodsCount'] = self.confirmGoodsCount
        json_data['Oldprice'] = self.oldprice
        json_data['Shopname'] = self.shopname
        print json_data
        json_str = json.dumps(json_data)
        print(json_str)

        for i in self.newid:
            self.redis_api.add('newid', i)
        self.redis_api.add('doneid', self.id)

    def getInfo(self):
        request = urllib2.Request(self.index_url, headers=self.header)
        response = urllib2.urlopen(request)
        page = response.read().decode('gbk')
        soup = BeautifulSoup(page, 'html.parser')
        temp = soup.select('meta')
        pa1 = r'.*?shopId=(.*?);userid=(.*?);.*?'
        pattern1 = re.compile(pa1, re.S)
        temp = re.findall(pattern1, str(temp[8]))
        temp = str(temp[0]).strip('()').split(',')
        self.shopid = temp[0].strip(' ').strip('\'')
        self.userid = temp[1].strip(' ').strip('\'')

        self.__init____()

        soup = BeautifulSoup(page, 'html.parser')
        shop = soup.select('.tb-shop-name')
        pa1 = r'.*?<a.*?>(.*?)</a>.*?'
        pattern = re.compile(pa1, re.S)
        shopname = re.findall(pattern, str(shop))
        self.shopname = shopname[0].strip(' ').replace(' ', '').replace('\n', '')
        self.shopname=self.shopname.decode('unicode-escape').encode('utf-8').replace('\n', '')
        self.name = soup.select('h3')[0].text.strip()

        subtitle = soup.select('.tb-subtitle')
        pa1 = r'.*?<p.*?>(.*?)</p>.*?'
        pattern = re.compile(pa1, re.S)
        result = re.findall(pattern, str(subtitle[0]))
        self.descripe = result[0]  # 商品描述

    def getPrice(self):
        request = urllib2.Request(url=self.price_url, headers=self.header)
        response = urllib2.urlopen(request)
        page = response.read().decode('gbk')
        jsondata = json.loads(page[22:-2])
        self.soldCount = jsondata['data']['soldQuantity']['soldTotalCount']  # 一月售出
        self.confirmGoodsCount = jsondata['data']['soldQuantity']['confirmGoodsCount']  # 交易成功
        self.oldprice = jsondata['data']['price']  # 原价

        pa = r'.*?"loginPromotion":false,"price":"(.*?)","start":false.*?'
        pattern = re.compile(pa, re.S)
        result = re.findall(pattern, page)
        self.price = result[0]  # 价格

    def getMoreId(self):
        request = urllib2.Request(url=self.recommend_url, headers=self.header)
        response = urllib2.urlopen(request)
        page = response.read().decode('gbk')
        jsondata = json.loads(page[14:-2])
        for i in jsondata['result']:  # 推荐商品
            self.newid.append(i['itemId'])
        request = urllib2.Request(url=self.neighbor_url, headers=self.header)
        response = urllib2.urlopen(request)
        page = response.read().decode('gbk')
        jsondata = json.loads(page[12:-2])
        for i in jsondata['result']:
            self.newid.append(i['itemId'])


class Spider(object):
    def __init__(self, startid, mongo_api, redis_api):
        self.startid = startid
        self.mongo_api = mongo_api
        self.redis_api = redis_api

    def Action(self):
        try:
            CrawlerTaobao(int(self.startid), redis_api, mongo_api).Action()
        except IndexError as e:
            print(e)
        except KeyError as e:
            print(e)
        except ssl.SSLEOFError as e:
            print(e)
        except urllib2.URLError as e:
            print(e)
            # while self.redis_api.number('newid') > 0:
            #     newid = self.redis_api.pop('newid')
            #     newid = int(newid)
            #     try:
            #         CrawlerTaobao(newid, redis_api, mongo_api).Action()
            #     except IndexError as e:
            #         print(e)
            #     except KeyError as e:
            #         print(e)
            #     except ssl.SSLEOFError as e:
            #         print(e)
            #     except urllib2.URLError as e:
            #         print(e)

            print('doneid:', self.redis_api.number('doneid'), ',newid:', self.redis_api.number('newid'), ',mongodhb:',
                  self.mongo_api.number())


def clearAll(redis_api, mongo_api):
    while redis_api.number('newid') > 0:
        redis_api.pop('newid')

    while redis_api.number('doneid') > 0:
        redis_api.pop('doneid')

    mongo_api.drop()


if __name__ == '__main__-':
    redis_api = api.redis.RedisAPI('127.0.0.1', 6379)
    mongo_api = api.mongodb.MongoAPI("127.0.0.1", 27017, "taobao", "tb1")
    print('clear all')
    clearAll(redis_api, mongo_api)

if __name__ == '__main__':
    startid = 545265395724
    redis_api = api.redis.RedisAPI('127.0.0.1', 6379)
    mongo_api = api.mongodb.MongoAPI("127.0.0.1", 27017, "taobao", "tb1")

    spider = Spider(startid, mongo_api, redis_api)
    spider.Action()
