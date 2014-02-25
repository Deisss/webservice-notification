# Server

This is the entry point for the notification server.

This server is a full python/MongoDB system. It needs the following pip installation:

```
pip install tornado pymongo sockjs-tornado sockjsroom PyDispatcher
```

And a configuration file setted on ```config.ini```.


## How to use

From a server you already have, you want to implement a notification system on top of your existing system: you simply want to do a POST request on ```/notify``` to register a new notification to listed users.

On the other side (client side), users have to subscribe to websocket provided by this server.

For more information, just go to main [README.md file](https://github.com/Deisss/webservice-notification) 