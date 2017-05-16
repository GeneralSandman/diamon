#! /usr/bin/env python
# coding=utf-8

import optparse
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver
import redis
import pymongo


def parse_args():
    usage = """usage: %prog [options]

This is the Poetry Transform Server.
Run it like this:

  python transformedpoetry.py

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-server-1/transformedpoetry.py --port 11000

to provide poetry transformation on port 11000.
"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option('--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option('--iface', help=help, default='localhost')

    options, args = parser.parse_args()

    if len(args) != 0:
        parser.error('Bad arguments.')

    return options


class MongoAPI(object):
    def __init__(self, db_ip, db_port, db_name, table_name):
        self.db_ip = db_ip
        self.db_port = db_port
        self.db_name = db_name
        self.table_name = table_name
        self.conn = pymongo.MongoClient(host=self.db_ip, port=self.db_port)  # 创建链接
        self.db = self.conn[self.db_name]  # 选择数据库
        self.table = self.db[self.table_name]  # 选择集合

    def get_one(self, query):
        return self.table.find_one(query, projection={"_id": False})

    def get_all(self, query):
        return self.table.find(query)

    def add(self, kv_dict):
        return self.table.insert(kv_dict)

    def drop(self):
        return self.table.remove({})

    def number(self):
        return self.table.count()

    def delete(self, query):
        return self.table.delete_many(query)

    def check_exist(self, query):
        ret = self.get(query)
        return len(ret) > 0

    # 如果没有 会新建
    def update(self, query, kv_dict):
        ret = self.table.update_many(
            query,
            {
                "$set": kv_dict,
            }
        )
        if not ret.matched_count or ret.matched_count == 0:
            self.add(kv_dict)
        elif ret.matched_count and ret.matched_count > 1:
            self.delete(query)
            self.add(kv_dict)


class RedisAPI(object):
    def __init__(self, redis_host, redis_port):
        self.pool = redis.ConnectionPool(host=redis_host, port=redis_port)
        self.conn = redis.Redis(connection_pool=self.pool)

    def add(self, collection, newid):
        self.conn.sadd(collection, newid)

    def pop(self, collection):
        return self.conn.spop(collection)

    def number(self, collection):
        return self.conn.scard(collection)


class CrawlerServerProtocol(NetstringReceiver):
    def connectionMade(self):
        print('one connection:%s' % self.transport.getPeer())

    def stringReceived(self, string):
        print(string)
        if '.' not in string:
            self.sendString('form is error')
            return

        header, data = string.split('.', 1)
        self.serviceResponse(header, data)

    def serviceResponse(self, header, data):
        response = self.factory.serviceResponse(header, data)

        if response is not None:
            self.sendString(response)


class CrawlerServerFactory(ServerFactory):
    protocol = CrawlerServerProtocol

    def __init__(self, service):
        self.service = service

    def serviceResponse(self, header, data):
        attr = getattr(self, ('response_%s') % header)

        if attr is None:
            return None

        try:
            return attr(data)
        except:
            return None  # transform failed

    def response_GetTaskId(self, data):
        print('give you one id')
        return self.service.returnTaskId()

    def response_SubmitNewId(self, data):
        return self.service.storeNewId(data)

    def response_ReturnDoneId(self, data):
        return self.service.storeDoneId(data)


class Service(object):
    def __init__(self, redis_api, mongo_api):
        self.redis_api = redis_api
        self.mongo_api = mongo_api

    def storeDoneId(self, data):
        doneid = int(data)
        self.redis_api.add('doneid', doneid)
        return None

    def returnTaskId(self):
        response = 'ResponseTaskId'
        newid = 0
        if self.redis_api.number('newid') > 0:
            newid = self.redis_api.pop('newid')

        if newid is not 0:
            response = response + '.' + str(newid)
        else:
            response = response + '.' + 'NoMoreId'

        return response

    def storeNewId(self, data):
        newids = data.split(',')
        for i in newids:
            if len(i) is not 0:
                self.redis_api.add('newid', int(i))

        return None


def main():
    redis_api = RedisAPI('127.0.0.1', 6379)
    mongo_api = MongoAPI("127.0.0.1", 27017, "taobao", "tb1")

    options = parse_args()

    service = Service(redis_api, mongo_api)

    factory = CrawlerServerFactory(service)

    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0, factory,
                             interface=options.iface)

    print('Serving transforms on %s.' % (port.getHost(),))

    reactor.run()


if __name__ == '__main__':
    main()
