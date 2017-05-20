#! /usr/bin/env python
# coding=utf-8


import urllib2
import sys
import re
import json
from bs4 import BeautifulSoup

from basicCrawler import Crawler

header = {
    'referer': 'https://detail.tmall.com/item.htm?id=522128736149',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537\
                        .36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
    'cookie': '__jdv=122270672|www.shenjianshou.cn|-|referral|-|1494932842923; ipLoc-djd=1-72-2799-0; __jda=122270672.1494932842919250345233.1494932843.1494932843.1494932843.1; __jdb=122270672.5.1494932842919250345233|1.1494932843; __jdc=122270672; 3AB9D23F7A4B3C9B=ZTFV5ON3CG2LCT'
              'EETWF5QWOEIPCDJAPHJZPVGDPDZCG4CPRCMPVJDK7V7VYJ5CQRW74HKMY5EFIBU7UYRPCCMZXYSY; __jdu=1494932842919250345233'
}


class CrawlerTM(Crawler):
    index_url_format = 'https://detail.tmall.com/item.htm?id={Id}'
    recommend_url_format1 = 'https://ext-mdskip.taobao.com/extension/queryTmallCombo.do?&callback=jsonp2358&itemId={Id}'
    recommend_url_format2 = 'https://aldcdn.tmall.com/recommend.htm?itemId={Id}&categoryId=50011123&sellerId=1022008754&shopId=73200079&brandId' \
                            '=29483&refer=&brandSiteId=0&rn=&appId=03054&isVitual3C=false&isMiao=false&count=15&callback=jsonpAld03054'
    # we have to format sellerid shopid
    price_url_format = 'https://mdskip.taobao.com/core/initItemDetail.htm?itemId={Id}&callback=setMdskip'
    sellcount_url_format = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId={Id}&spuId=418408433&sellerId=1022008754&callback=jsonp229'
    header = {
        'referer': '',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537\
                            .36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
        'cookie': '__jdv=122270672|www.shenjianshou.cn|-|referral|-|1494932842923; ipLoc-djd=1-72-2799-0; __jda=122270672.1494932842919250345233.1494932843.1494932843.1494932843.1; __jdb=122270672.5.1494932842919250345233|1.1494932843; __jdc=122270672; 3AB9D23F7A4B3C9B=ZTFV5ON3CG2LCT'
                  'EETWF5QWOEIPCDJAPHJZPVGDPDZCG4CPRCMPVJDK7V7VYJ5CQRW74HKMY5EFIBU7UYRPCCMZXYSY; __jdu=1494932842919250345233'
    }

    def __init__(self, id, mongo_api):
        self.id = id
        self.mongo_api = mongo_api
        self.index_url = self.index_url_format.format(Id=self.id)
        self.recommend_url1 = self.recommend_url_format1.format(Id=self.id)
        self.recommend_url2 = self.recommend_url_format2.format(Id=self.id)
        self.price_url = self.price_url_format.format(Id=self.id)
        self.sellcount_url = self.sellcount_url_format.format(Id=self.id)
        self.header['referer'] = self.index_url

        self.name = ''
        self.shopname = ''
        self.shopid = 0
        self.soldCount = 0
        self.oldprice = 0
        self.price = 0
        self.newids = []
        self.gradeAvg = 0
        self.rateTotal = 0

    def __init____(self):
        pass

    def Action(self):
        self.getInformation()
        self.printInfomation()
        self.storeInformation()

    def getInformation(self):

        def getName():
            request = urllib2.Request(url=self.index_url, headers=header)
            response = urllib2.urlopen(request)
            page = response.read().decode('gbk')
            soup = BeautifulSoup(page, 'html.parser')
            self.name = soup.select('title')[0].text[0:-12]
            self.shopname = soup.select('.slogo-shopname')[0].text

        def getPrice():
            import random
            request = urllib2.Request(url=self.price_url, headers=header)
            response = urllib2.urlopen(request)
            page = response.read().decode('gbk')
            # print page[12:-1]
            jsondata = json.loads(page[12:-1])
            self.soldCount = jsondata['defaultModel']['sellCountDO']['sellCount']
            price = jsondata['defaultModel']['itemPriceResultDO']['priceInfo']
            key = random.choice(price.keys())
            self.oldprice = price[key]['price']  # old
            self.price = price[key]['promotionList'][0]['price']

        def getComment():
            request = urllib2.Request(url=self.sellcount_url, headers=header)
            response = urllib2.urlopen(request)
            page = response.read().decode('gbk')
            # print page[9:-2]
            jsondata = json.loads(page[9:-2])
            self.gradeAvg = jsondata['dsr']['gradeAvg']
            self.rateTotal = jsondata['dsr']['rateTotal']

        def getRecommend1():
            request = urllib2.Request(url=self.recommend_url1, headers=header)
            response = urllib2.urlopen(request)
            page = response.read().decode('gbk')
            # print page[12:-1]
            jsondata = json.loads(page[12:-1])
            if jsondata['currentCombo']['items'] is not None:
                for i in jsondata['currentCombo']['items']:
                    self.newids.append(i.encode('utf-8'))

        def getRecommend2():
            request = urllib2.Request(url=self.recommend_url2, headers=header)
            response = urllib2.urlopen(request)
            page = response.read().decode('gbk')
            # print page[16:-1]
            jsondata = json.loads(page[16:-1])

            pa = r'.*?pvid.*?id=(.*?)&scm.*?'
            pattern = re.compile(pa, re.S)

            for i in jsondata['list']:
                url = i['url'].encode('utf-8')
                id = re.findall(pattern, url)
                self.newids.append(id[0])

        getName()
        self.__init____()
        getPrice()
        getComment()
        getRecommend1()
        getRecommend2()

    def printInfomation(self):
        print'Id:', self.id, type(self.id)
        print'商品名称:', self.name, type(self.name)
        print'店铺名称:', self.shopname, type(self.shopname)
        print'销量:', self.soldCount, type(self.soldCount)
        print'评分:', self.gradeAvg, type(self.gradeAvg)
        print'原价:', self.oldprice, type(self.oldprice)
        print'现价:', self.price, type(self.price)
        print'好评率:', self.rateTotal, type(self.rateTotal)
        print'Newid:', len(self.newids), self.newids, type(self.newids[0])

    def storeInformation(self):
        self.mongo_api.add({'商品ID': self.id, '商品名称': self.name, '价格': self.price, '评分': self.gradeAvg,
                            '销量': int(self.soldCount), '好评率': self.rateTotal, '原价': int(self.oldprice),
                            '店铺': self.shopname})

    def generateNewId(self):
        return self.newids


if __name__ == "__main__":
    pass
