#! /usr/bin/env python
# coding=utf-8

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, defer


class ItemServerProtocol(Protocol):
    def connectionMade(self):
        print('')

    def connectionLost(self, reason):
        print('')

    def dataReceived(self, data):
        pass


class ItemServerFactory(Factory):
    protocol = ItemServerProtocol

    def __init__(self, defer):
        self.defer = defer


def getItems():
    d = defer.Deferred()
    factory = ItemServerFactory()
    reactor.listenTCP(8081, factory)
    reactor.run()
    return d


def main():
    getItems()


if __name__ == '__main__':
    main()
