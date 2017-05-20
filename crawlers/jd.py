#! /usr/bin/env python
# coding=utf-8


import urllib2
import sys
import re
from bs4 import BeautifulSoup

from basicCrawler import Crawler




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
