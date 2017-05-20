#! /usr/bin/env python
# coding=utf-8

import optparse
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver
from api.mongodb import MongoAPI
from api.redis import RedisAPI


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

    def connectionLost(self, reason):
        pass
        # recover taskid

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
    def __init__(self, redis_api):
        self.redis_api = redis_api

    def storeDoneId(self, data):
        doneid = int(data)
        self.redis_api.add('doneid', doneid)
        return None

    def recoverTaskId(self, data):
        pass
        # handle the coonection lost
        # recover the taskid

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
