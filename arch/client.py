#! /usr/bin/env python
# coding=utf-8


import urllib2
import re
from bs4 import BeautifulSoup
import json
import ssl
import optparse
from twisted.protocols.basic import NetstringReceiver
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, defer

newids = []


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, Twisted version 4.0
Run it like this:

  python get-poetry.py port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-client-4/get-poetry.py 10001 10002 10003

to grab poetry from servers on ports 10001, 10002, and 10003.

Of course, there need to be servers listening on those ports
for that to work.
"""

    parser = optparse.OptionParser(usage)

    _, addresses = parser.parse_args()

    if not addresses:
        print(parser.format_help())
        parser.exit()

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return map(parse_address, addresses)


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

    def __init__(self, id):
        self.id = id
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
        # self.printInformation()
        self.storeInformation()
        global newids
        newids = self.newid

    def getInformation(self):
        self.getInfo()
        self.getPrice()
        self.getMoreId()

    def returnNewIds(self):
        newids = self.newid

    def printInformation(self):
        print('Id:', self.id, type(self.id))
        print('商品名称:', self.name, type(self.name))
        print('店铺名称:', self.shopname, type(self.shopname))
        print('商品描述:', self.descripe, type(self.descripe))
        print('销量:', self.soldCount, type(self.soldCount))
        print('交易成功:', self.confirmGoodsCount, type(self.confirmGoodsCount))
        print('原价:', self.oldprice, type(self.oldprice))
        print('现价:', self.price, type(self.price))
        print('Newid:', len(self.newid), self.newid, type(self.newid[0]))

    def storeInformation(self):
        pass

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

        shop = soup.select('.tb-shop-name')
        pa1 = r'.*?<a.*?>(.*?)</a>.*?'
        pattern = re.compile(pa1, re.S)
        shopname = re.findall(pattern, str(shop))
        self.shopname = shopname[0].strip(' ').replace(' ', '').strip('\n')
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


class CrawlerClientProtocol(NetstringReceiver):
    def connectionMade(self):
        self.sendString('GetTaskId.')

    def stringReceived(self, string):
        print (string)
        if '.' not in string:
            self.sendString('form is error')
            return

        header, data = string.split('.', 1)
        self.serviceResponse(header, data)

    def serviceResponse(self, header, data):
        responses = self.factory.serviceResponse(header, data)

        for res in responses:
            if res is not None:
                self.sendString(res)


class CrawlerClientFactory(ClientFactory):
    protocol = CrawlerClientProtocol

    def __init__(self, d, service):
        self.defer = d
        self.service = service

    def serviceResponse(self, header, data):
        responses = []

        try:
            self.service.parserOneGoods(data)

        except IndexError as e:
            print(e)
        except KeyError as e:
            print(e)
        except ssl.SSLEOFError as e:
            print(e)
        except urllib2.URLError as e:
            print(e)
        else:
            submitNewid = self.service.submitNewId(data)
            returnDoneid = self.service.returnDoneId(data)
            responses.append(submitNewid)
            responses.append(returnDoneid)

        return responses

    def poem_finished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)


class Service(object):
    def parserOneGoods(self, data):
        CrawlerTaobao(int(data)).Action()

    def submitNewId(self, data):
        response = 'SubmitNewId.'
        for i in newids:
            response = response + str(i) + ','
        return response

    def returnDoneId(self, data):
        response = 'ReturnDoneId.'
        response += str(data)
        return response

    def returnFailId(self, data):
        response = 'ReturnFailId.'
        response += str(data)
        return response


def getTask(host, port):
    d = defer.Deferred()
    service = Service()
    factory = CrawlerClientFactory(d, service)
    reactor.connectTCP(host, port, factory)
    return d


def main():
    # addresss = parse_args()

    host = '127.0.0.1'
    port = 10001

    d = getTask(host, port)

    reactor.run()


if __name__ == '__main__':
    main()
