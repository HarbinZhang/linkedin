#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scawler import Scawler


username = 'haibin610@yeah.net'
password = 'coolman'
url = 'https://www.linkedin.com/in/haibinzhang'


if __name__ == '__main__':
    scawler = Scawler(username,password)
    scawler.deal(10)
    # scawler.dealNew(url)

    # ceshi"url_id" : "haibinzhang"
    # soup = scawler.preLoad(url)
    # print scawler.getSkills(soup)
