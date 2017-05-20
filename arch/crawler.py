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
import crawlers.taobao

startid = 545265395724
redis_api = RedisAPI('127.0.0.1', 6379)
mongo_api = MongoAPI("127.0.0.1", 27017, "taobao", "tb1")

spider = Spider(startid, mongo_api, redis_api)

crawler=CrawlerTaobao()