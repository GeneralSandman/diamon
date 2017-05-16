#! /usr/bin/env python
# coding=utf-8

import parser

data = '6231872,12736,324123,123412,3123,'

data = data.split(',')

for i in data:
    if len(i) is not 0:
        print(i,'--')
