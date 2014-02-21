#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sockjsroom import SockJSDefaultHandler
from bson.json_util import dumps
from pydispatch import dispatcher
from system.ConfigLoader import getCfg
from system.CommonMySQL import loginUser
from system.CommonMongoDB import createNotification, getUserUnseenNotifications, getUserNotifications, seenNotification, deleteNotification

import logging

def _debug(str):
    logging.debug('notification: ' + str)


class NotificationSocketHandler(SockJSDefaultHandler):
    ''' Basic notification system '''
    #
    # ---------------------------
    #   CLASS INIT
    # ---------------------------
    #
    def initialize(self):
        ''' Initialize any new connection '''
        self.login    = ''
        # As we use the str() function, the None is never really None
        # So we use this also here to keep test simple
        self.userId   = 'None'

    def startPubSub(self):
        ''' Starting the PubSub system '''
        if self.userId != 'None':
            _debug('start pubsub for user #%s (%s)'
                            % (self.userId, self.login))
            dispatcher.connect(
                self.pubsub,
                signal='user-%s' % self.userId
            )

    def stopPubSub(self):
        ''' Stopping the PubSub system '''
        if self.userId != 'None':
            _debug('stop pubsub for user #%s (%s)'
                            % (self.userId, self.login))
            dispatcher.disconnect(
                self.pubsub,
                signal='user-%s' % self.userId
            )

    def jsonSend(self, name, param):
        ''' Publish as JSON data '''
        self.send({
            'name': name,
            'data': SockJSDefaultHandler._parser.encode(list(param))
        })

    #
    # ---------------------------
    #   SOCKJS DEFAULT FUNCTION
    # ---------------------------
    #
    def on_open(self, info):
        pass

    def on_close(self):
        self.on_leave()

    #
    # ---------------------------
    #   SOCKJS CUSTOM FUNCTION
    # ---------------------------
    #
    def on_join(self, data):
        ''' Join the notification system '''
        # data => login, password
        self.initialize()

        # Get the login and password, and check user on database
        self.login    = str(data['login'])
        self.userId   = str(loginUser(self.login, str(data['password'])))



        if self.userId != 'None':
            _debug('joining user #%s (%s)' % (self.userId, self.login))
            self.startPubSub()

            # We send back the unseen notifications
            self.on_unseen(None)
        else:
            _debug('ERROR joining user #%s (%s)' % (self.userId, self.login))
            self.initialize()


    def on_seen(self, data):
        ''' User seen a new notification, we mark them as seen '''
        # data => [id(s)], list of ids to mark as seen
        if self.userId != 'None':
            _debug('user #%s (%s) ask to mark as seen %s'
                        % (self.userId, self.login, data['ids']))
            seenNotification(self.userId, data['ids'])
            self.jsonSend('seen', data['ids'])


    def on_delete(self, data):
        ''' User want to delete some notifications, we mark them as deleted '''
        # data => [id(s)], list of ids to mark as delete
        if self.userId != 'None':
            _debug('user #%s (%s) ask to mark as delete %s'
                        % (self.userId, self.login, data['ids']))
            deleteNotification(self.userId, data['ids'])
            self.jsonSend('delete', data['ids'])


    def on_unseen(self, data):
        ''' Get the unseen content only '''
        # data => unused
        if self.userId != 'None':
            userNotification = getUserUnseenNotifications(self.userId)
            self.jsonSend('notification', userNotification)


    def on_content(self, data):
        ''' User ask to get latests notifications '''
        # data => page, limit
        if self.userId != 'None':
            page  = int(data['page'])
            limit = getCfg('APPLICATION', 'limit', 'int')

            # Make elements fit requirements
            page  = max(0, page)
            limit = max(1, limit)
            limit = min(100, limit)

            # Get latests notifications for user, and send it back
            userNotification = getUserNotifications(self.userId, page, limit)
            self.jsonSend('notification', userNotification)


    def pubsub(self, sender, data):
        '''
            This function send a notification from pubsub system
            to user, as the pubsub is not a socket element, we are
            not using the on_* pattern (we don't want user to be
            able to request himself this function threw client side)
        '''
        if self.userId != 'None':
            _debug('pubsub user #%s (%s):\n\tmessage:%s'
                            % (self.userId, self.login, data))
            self.jsonSend('notification', [data])


    def on_leave(self):
        ''' Leave the notification system '''
        # Only if user has time to call self.initialize
        # (sometimes it's not the case)
        if self.userId != 'None':
            _debug('leaving user #%s (%s)' % (self.userId, self.login))
            self.stopPubSub()
            # Erasing data
            self.initialize()
