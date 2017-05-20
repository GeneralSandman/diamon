#! /usr/bin/env python
# coding=utf-8

import redis


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
