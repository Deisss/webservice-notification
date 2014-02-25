#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sockjsroom import JsonDefaultHandler
from pydispatch import dispatcher
from datetime   import datetime

from system.CommonMongoDB import createNotification
from system.EmailNotification import send

import json, logging

'''
A notification is represented by:
> automatically populated
    _id       (ObjectId)
    createdAt (date)
    updatedAt (date)
    deletedAt (date)
    delete    (Boolean)
    seen      (Boolean)
    _userId   (str) => the userid linked to...

> defined by service
    type      (String - a custom type)
    title     (String)
    content   (String)
    url       (String)
    icon      (String - an icon to show)
    image     (String - an image to show, like user profile)

> Except content, all of them are optionals, and system does't use them
They are here to help you define your own client look
'''

def getBooleanRealValue(b):
    ''' Simple string to boolean convertion '''
    if b == True or b == '1' or b == 1 or b == 'true' or b == 'True' or b == 'yes' or b == 'Yes':
        return True
    else:
        return False


class ServiceRequestManager(JsonDefaultHandler):
    ''' Register a notification to user '''
    def post(self):
        # Will throw an HTTP 400 if missing
        content = self.get_argument('content')

        # TYPE: the notification type
        custom  = self.get_argument('type', '')
        # TITLE: the notification title - can be null
        title   = self.get_argument('title', '')
        # URL: a link to the given notification - can be null
        url     = self.get_argument('url', '')
        # ICON: a class/image or something to show as icon - can be null
        icon    = self.get_argument('icon', '')
        # IMAGE: an image to represent post (like user on fb) - can be null
        image   = self.get_argument('image', '')
        # Users linked to the notification (user should recieve notification)
        users   = json.loads(self.get_argument('users', '[]'))


        if len(users) == 0:
            logging.error('notify: NO USER SPECIFIED, you have to specify: ' +
                'at least one:' +
                '\n\ttitle: %s\n\turl: %s\n\tcontent: %s\n'
                % (title, url, content))



        # Email stuff
        # System should send an email...
        canEmail   = self.get_argument('email_send', False)
        forceEmail = self.get_argument('email_force', False)
        # Check everything is fine
        canEmail   = getBooleanRealValue(canEmail)
        forceEmail = getBooleanRealValue(forceEmail)

        # ForceEmail will always override canEmail as it is mandatory
        if forceEmail == True:
            canEmail = True

        emailSubject = self.get_argument('email_subject', '')
        emailContent = self.get_argument('email_content', '')
        emailMime    = self.get_argument('email_mime', '1.0')
        emailType    = self.get_argument('email_type', 'text/html')



        # Debug (if needed)
        logging.debug('notify: new notification: ' +
            '\n\ttitle: %s\n\turl: %s\n\tcontent: %s\n'
            % (title, url, content))

        # This element will recieve all notification to send to user
        notifications = []
        unsent = []

        for user in users:
            # Get user information
            userId    = str(user['id'])
            userEmail = user['email']
            signal    = 'user-%s' % userId

            # We check if there is one socket binded to given signal
            reciever = len(dispatcher.getReceivers(signal=signal))

            notifications.append({
                'type':    custom,
                'title':   title,
                'content': content,
                'url':     url,
                'icon':    icon,
                'image':   image,
                '_userId': userId
            })

            # Append the user to next email campaign if needed
            if reciever <= 0 or forceEmail == True:
                unsent.append(userEmail)



        # We bulk insert everything in a single call to database
        # No matter if user is connected or not, we need to try...
        if len(notifications) > 0:
            createNotification(notifications)

            # For every item in notifications, we send them threw dispatcher
            # to let socket know if there is something to update
            for notification in notifications:
                data = {
                    'data': notification
                }
                userId = notification['_userId']
                signal = 'user-%s' % userId
                dispatcher.send(
                    signal=signal,
                    sender=dispatcher.Anonymous,
                    **data
                )



        # We send email to people not connected
        if len(unsent) > 0 and canEmail == True:
            send(unsent, emailSubject, emailContent, emailType, emailMime)