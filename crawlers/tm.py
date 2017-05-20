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
    pass


def getName():
    index_url = 'https://detail.tmall.com/item.htm?id=522128736149'
    request = urllib2.Request(index_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    soup = BeautifulSoup(page, 'html.parser')
    name = soup.select('title')[0].text[0:-12]
    shopname = soup.select('.slogo-shopname')[0].text
    print shopname
    print name


def getComment():
    comment_url = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=522128736149&spuId=418408433&sellerId=1022008754&_ksTS=1495267599070_228&callback=jsonp229'
    request = urllib2.Request(comment_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    # print page[9:-2]
    jsondata = json.loads(page[9:-2])
    gradeAvg = jsondata['dsr']['gradeAvg']
    rateTotal = jsondata['dsr']['rateTotal']
    print gradeAvg
    print rateTotal


def getSellCountPrice():
    import random
    sell_url = 'https://mdskip.taobao.com/core/initItemDetail.htm?isPurchaseMallPage=false&isUseInventoryCenter=false&isSecKill=false&household=false&queryMemberRight=true&cachedTimestamp=1495279140376&cartEnable=true&itemId=522128736149&tmallBuySupport=true&addressLevel=2&showShopProm=false&isRegionLevel=false&service3C=false&tryBeforeBuy=false&sellerPreview=false&isApparel=true&isForbidBuyItem=false&isAreaSell=false&offlineShop=false&callback=setMdskip&timestamp=1495279140862&isg=AsHBNSHhTeXGMNvk-vL0WLGeUQfavjXF&isg2=ArCw76OZnZNA6UGormbj277BgXcWEJRDpB2Bc6oALIv7ZVAPUglk0wYVy9r_'
    request = urllib2.Request(sell_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    print page[12:-1]
    jsondata = json.loads(page[12:-1])
    sellCount = jsondata['defaultModel']['sellCountDO']['sellCount']
    price = jsondata['defaultModel']['itemPriceResultDO']['priceInfo']
    key = random.choice(price.keys())
    oldPrice=price[key]['price'] #old
    price=[key]['promotionList'][0]['price']
    print sellCount
    print oldPrice
    print price



def getPrice():
    url = 'https://mdskip.taobao.com/core/initItemDetail.htm?isPurchaseMallPage=false&isUseInventoryCenter=false&isSecKill=false&household=false&queryMemberRight=true&cachedTimestamp=1495279140376&cartEnable=true&itemId=522128736149&tmallBuySupport=true&addressLevel=2&showShopProm=false&isRegionLevel=false&service3C=false&tryBeforeBuy=false&sellerPreview=false&isApparel=true&isForbidBuyItem=false&isAreaSell=false&offlineShop=false&callback=setMdskip&timestamp=1495280805834&isg=AkZGJcglUqSFeXx1Ceu7eVgGFjbLhYrS&isg2=At7eZdW0CylIdl_yTEC1MXyPL300dqIZJqM_yYhkaCGvq3yF8y2MKSUL1QBd'
    request = urllib2.Request(url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    print page


def getRecommend():
    commend_url = 'https://ext-mdskip.taobao.com/extension/queryTmallCombo.do?areaId=370100&comboId=&noCache=false&_ksTS=1495277889656_2357&callback=jsonp2358&itemId=522128736149&comboGroup=0&isg=AvHxqur-DKBeQ6CLtyGSyHc-AHSfN5WEHZJgUNMG1rjb-hFMGy51IJ8cajlm&isg2=AnR0pPxCoFKDQ04r1%2FFpTxMoxDjmdpg7'
    request = urllib2.Request(commend_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    # print page[12:-1]
    jsondata = json.loads(page[12:-1])
    for i in jsondata['currentCombo']['items']:
        print i.encode('utf-8')


def getRecommend1():
    commend_url = 'https://aldcdn.tmall.com/recommend.htm?itemId=522128736149&categoryId=50011123&sellerId=1022008754&shopId=73200079&brandId=29483&refer=&brandSiteId=0&rn=&appId=03054&isVitual3C=false&isMiao=false&count=15&callback=jsonpAld03054'
    request = urllib2.Request(commend_url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    # print page[16:-1]
    jsondata = json.loads(page[16:-1])

    pa = r'.*?pvid.*?id=(.*?)&scm.*?'
    pattern = re.compile(pa, re.S)

    for i in jsondata['list']:
        url = i['url'].encode('utf-8')
        id = re.findall(pattern, url)
        print id[0]


def getshochang():
    import demjson

    url = 'https://count.taobao.com/counter3?_ksTS=1495280808062_252&callback=jsonp253&keys=SM_368_dsr-1022008754,ICCP_1_522128736149'
    request = urllib2.Request(url, headers=header)
    response = urllib2.urlopen(request)
    page = response.read().decode('gbk')
    print page[9:-2]
    jsondata = demjson.encode(page[9:-2].encode('utf-8'))
    print jsondata
    shochang = jsondata["ICCP_1_522128736149"]
    # bug
    print shochang


if __name__ == "__main__":
    getName()
