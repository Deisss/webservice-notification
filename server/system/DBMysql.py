#!/usr/bin/env python
# -*- coding: utf-8 -*-


import MySQLdb as db
from system.ConfigLoader import getCfg




def connect():
    ''' Create a new connection with MySQL '''
    # Set parameter format
    db.paramstyle = 'format'
    # Get connection
    return db.connect(
        host   = getCfg('MYSQL', 'host'),
        user   = getCfg('MYSQL', 'user'),
        passwd = getCfg('MYSQL', 'password'),
        db     = getCfg('MYSQL', 'db'),
        port   = getCfg('MYSQL', 'port', 'int'),

        # Force UTF 8
        charset= 'utf8',
        init_command='SET NAMES UTF8'
    )

    


