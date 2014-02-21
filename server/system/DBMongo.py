#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo

from system.ConfigLoader import getCfg




def connect(collection):
    ''' Connect to a database, and give back collection '''
    url = getCfg('MONGODB', 'url')
    name = getCfg('MONGODB', 'db')

    # Make url compatible in all cases with name
    if url[-1:] != '/':
        url += '/'

    con = pymongo.MongoClient(url + name, getCfg('MONGODB', 'port', 'int'))
    db = con[name]
    return db[collection]
