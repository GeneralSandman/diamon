#! /usr/bin/env python
# coding=utf-8

from api.mongodb import MongoAPI
from api.redis import RedisAPI
from crawlers.taobao import CrawlerTaobao
import ssl
import urllib2
from crawlers.jd import CrawlerJD
from crawlers.tm import CrawlerTM


class Spider(object):
    def __init__(self, startid, mongo_api, redis_api):
        self.startid = startid
        self.mongo_api = mongo_api
        self.redis_api = redis_api

    def Action(self):
        try:
            CrawlerTaobao(int(self.startid), mongo_api).Action()
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


def testTB():
    pass


def testJD():
    pass


def testTM():
    pass


if __name__ == '__main__-':
    redis_api = RedisAPI('127.0.0.1', 6379)
    mongo_api = MongoAPI("127.0.0.1", 27017, "taobao", "tb1")
    print('clear all')
    clearAll(redis_api, mongo_api)

if __name__ == '__main__':
    startid = 545265395724
    redis_api = RedisAPI('127.0.0.1', 6379)
    mongo_api = MongoAPI("127.0.0.1", 27017, "taobao", "tb1")

    spider = Spider(startid, mongo_api, redis_api)
    spider.Action()
