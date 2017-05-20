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

from crawlers.taobao import CrawlerTaobao

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
