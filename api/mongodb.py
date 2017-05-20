#! /usr/bin/env python
# coding=utf-8

import pymongo

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
