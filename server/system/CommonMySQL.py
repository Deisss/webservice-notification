#!/usr/bin/env python
# -*- coding: utf-8 -*-

from system.DBMysql import connect
from system.ConfigLoader import getCfg

def loginUser(login, password):
    ''' Try to login a user regarding login/password '''
    userContent = None

    table         = getCfg('MYSQL', 'table')
    tableId       = getCfg('MYSQL', 'idField')
    tableLogin    = getCfg('MYSQL', 'loginField')
    tablePassword = getCfg('MYSQL', 'passwordField')

    try:
        # Starting
        con = connect()
        cur = con.cursor()

        cur.execute(
            'SELECT ' + tableId + ' FROM ' + table +
            ' WHERE ' + tableLogin + '=%s AND ' + tablePassword + '=%s',
            (
                login,
                password
            )
        )

        userContent = cur.fetchone()

        if userContent is not None:
            userContent = userContent[0]
        
    except db.Error as e:
        logging.error('loginUser: Error from MySQL => %s' % e)
    finally:
        if con:
            con.close()

    return userContent