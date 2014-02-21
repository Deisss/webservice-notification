#!/usr/bin/env python
# -*- coding: utf-8 -*-

from system.DBMongo import connect
from system.ConfigLoader import getCfg
from datetime import datetime
from bson.objectid import ObjectId

_collection = getCfg('MONGODB', 'db')

#
# ------------------------
#   NOTIFICATIONS
# ------------------------
#
def createNotification(notifications):
    ''' Register a new notification into database '''
    db  = connect(_collection)
    now = datetime.now()

    for notification in notifications:
        notification['createdAt'] = now
        notification['updatedAt'] = now
        notification['deletedAt'] = None
        notification['delete']    = False
        notification['seen']      = False

    db.insert(notifications, continue_on_error=True)

def getUserUnseenNotifications(userId):
    ''' Get the unseen notifications '''
    db = connect(_collection)

    return db.find({
        '_userId': str(userId),
        'seen':    False,
        'delete':  False
    }).sort('createdAt', 1)

def getUserNotifications(userId, page, limit):
    ''' Get many notifications linked to a user '''
    db = connect(_collection)

    return db.find({
        '_userId': str(userId),
        'delete':  False
    }).sort('createdAt', 1).skip(page * limit).limit(limit)

def seenNotification(userId, notificationsId):
    ''' Set many notifications as seen '''
    db  = connect(_collection)
    now = datetime.now()

    # We convert string ObjectId literals into ObjectId one
    resultsId = [ObjectId(str(x)) for x in notificationsId]

    db.update({
        '_id': {
            '$in': resultsId
        },
        '_userId': userId
    }, {
        '$set': {
            'seen':      True,
            'updatedAt': now
        }
    })

def deleteNotification(userId, notificationsId):
    ''' Set many notifications as delete '''
    db  = connect(_collection)
    now = datetime.now()

    # We convert string ObjectId literals into ObjectId one
    resultsId = [ObjectId(str(x)) for x in notificationsId]

    db.update({
        '_id': {
            '$in': resultsId
        },
        '_userId': userId
    }, {
        '$set': {
            'delete':    True,
            'deletedAt': now
        }
    })
