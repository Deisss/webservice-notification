# Client example


The client side is a simple example to manipulate two main functionnalities: the unseen notifications (all of them), and the first page only (as seen from API retrieve page by page).

_Note_: this example will probably not work with your system as **the client send password encrypted in SHA-512**. So be carefull, and check file ```action.js``` before doing anything.

_Note2_: jQuery is used only for DOM manipulation purpose, it's not required at all.

_Note3_: On the other side, sockjs framework IS needed (see ```index.html``` to get from CDN).

As this is an example, the ```notification.js``` and ```socket.js``` can be reused without modification into your own application, they are both framework-less (except SockJS). The last file ```action.js``` is this time specific to this demo page.
Here is a description of every files to get quickly into:


## Socket.js

A simple layer for [sockjsroom](https://github.com/Deisss/python-sockjsroom), this helps to use the multi-message and auto-reconnect capacities. It can be reused like this for every project you may have (the same file can be reused for all [sockjsroom](https://github.com/Deisss/python-sockjsroom) application).


## Notification.js

A layer for implementing API provided by this server, this should remains the same for your own application, it's not needed to change it as it is common to every application using this notification server.
Basically, it's just a simple object helping to connect/bind events/retrieve messages specifically from this server. To summarize: ```socket.js``` is fully generic to all [sockjsroom](https://github.com/Deisss/python-sockjsroom) application, ```notification.js``` is generic to all application using this server.


## Action.js

This file is _specific_ to this example, in this file you will find how to catch websocket events, and apply action to (basically DOM modification to graphically show notification to user).

In fact, a socket event (from ```notification.js```), will send on every example an object:
```js

// Bind to all notifications arriving
notification.bind(function(details) {
    // You can access to following content:
    details.element; // The given notification (system send them one by one)
    details.notification; // Same as element (alias)
    details.event; // The server event: 'seen', 'delete' or 'notification'
    details.seen; // Number of 'seen' notification currently stored on client side (see below)
    details.unseen; // Number of 'unseen' notification currently stored on client side (the most interesting)
    details.all; // Number of notifications (all of them) currently stored on client side
});

// Bind to only 'message' notification
notification.bind('message', function(details) {
    // Same details as above
});
```

**What is important here**, is the result difference between two binding:
**The second binding will only take care of notification with the 'message' type**. Others notifications will be ignored. This means that **details.seen, details.unseen, and details.all**, would be restricted to others type 'message', it means they will not have same number of elements compare to 'all' version.

This means you don't need to count how much items exist for every type, system will do it for you. And if you want to know all of them, just bind without any type...


### Why this behavior ?

The main example, will be of course, facebook:
  * You have notification for message, counting how many message are waiting your reply.
  * You have notification for everything else: somebody type on your wall, like your comment...

They are both counted separately. On this system, you should do something like this:
```js
notification.bind('message', function(details) {
    // Update facebook icon for messages
});

notification.bind('other', function(details) {
    // Update the 'global' notification system
    // If notification popup is show, update also this content with notification content
});
```

And on server side when you send a notification, you specify if it's a 'message' type or a 'other' type using the ```type``` parameter in ```/notify``` POST content.

If you understand this, you agree to the fact you don't want to have ALL unseen element for only message one, (you don't want to show 10 when you have 4 messages waiting, and 6 notifications, you want to show 4 message, and 6 notifications waiting instead).
This is why, if you bind only 'message' type, you will get only the statistics regarding this type.
