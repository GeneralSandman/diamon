#! /usr/bin/env python
# coding=utf-8




from crawlers.taobao import CrawlerTaobao
from api.mongodb import MongoAPI
from api.redis import RedisAPI

startid = 545265395724
redis_api = RedisAPI('127.0.0.1', 6379)
mongo_api = MongoAPI("127.0.0.1", 27017, "taobao", "tb1")

crawler = CrawlerTaobao(startid, mongo_api)
