#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging, tornado.web
from datetime import datetime

# Getting folder
fullPath = os.path.realpath(__file__)
dirPath  = os.path.dirname(fullPath)

# Register path
sys.path.append(os.path.join(dirPath, 'system' ))
sys.path.append(os.path.join(dirPath, 'handler'))

# Custom import
from handler.HTTPServer  import IndexHandler
from sockjs.tornado      import SockJSRouter
from system.ConfigLoader import getCfg

# Import sockets
from websocket  import NotificationSocketHandler
from webservice import ServiceRequestManager



def getLogLevel():
    ''' Get the current application minimum log level '''
    level = getCfg('LOG', 'level').lower()
    if level == 'info' or level == 'information':
        return logging.INFO
    elif level == 'warn' or level == 'warning':
        return logging.WARN
    elif level == 'error' or level == 'err':
        return logging.ERROR
    else:
        return logging.DEBUG



def configureLogger(_logFolder, _logFile):
    ''' Start the logger instance and configure it '''
    # Set debug level
    logger = logging.getLogger()
    logger.setLevel(getLogLevel())

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s | %(name)s -> %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )

    # Remove default handler to keep only clean one
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)

    # Create missing folder if needed
    if not os.path.exists(_logFolder):
        os.makedirs(_logFolder, 0700)

    #
    # ----------------------------
    #   CREATE CONSOLE HANDLER
    # ----------------------------
    #

    # Create console handler
    consoleh = logging.StreamHandler()
    consoleh.setLevel(getLogLevel())
    consoleh.setFormatter(formatter)

    # Set our custom handler
    logger.addHandler(consoleh)

    #
    # ----------------------------
    #   CREATE FILE HANDLER
    # ----------------------------
    #
    fileh = logging.FileHandler(_logFile, 'a')
    fileh.setLevel(getLogLevel())
    fileh.setFormatter(formatter)

    # Set our custom handler
    logger.addHandler(fileh)



def printWelcomeMessage(msg, place=10):
    ''' Print any welcome message '''
    logging.debug('*' * 30)
    welcome = ' ' * place
    welcome+= msg
    logging.debug(welcome)

    logging.debug('*' * 30 + '\n')







if __name__ == '__main__':
    logFile   = getCfg('LOG', 'file')
    logFolder = os.path.dirname(logFile)
    configureLogger(logFolder, logFile)

    serverPort = getCfg('APPLICATION', 'port', 'int')

    # Print logger message
    logging.debug('\n\nSystem start at: %s\nSystem log level: %s\n' %
                                (datetime.now(), getCfg('LOG', 'level')))

    printWelcomeMessage('STARTING',    11)
    printWelcomeMessage('SETUP ROUTES', 8)

    # Create route
    notifRouter = SockJSRouter(NotificationSocketHandler,  '/notification')

    # Create tornado app
    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/notify', ServiceRequestManager)
    ]
        + notifRouter.urls
    )

    # Listening to application
    app.listen(serverPort)

    printWelcomeMessage('SERVER RUNNING ON PORT %i' % serverPort, 1)

    # Start IOLoop
    tornado.ioloop.IOLoop.instance().start()