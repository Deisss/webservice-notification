# Client example


The client side is a simple example to manipulate the unseen elements (all of them), and the first page only (as seen from API retrieve page by page).

_Note_: this example can not work with your system as the client send password in SHA-512. So be carefull, and check file action.js before doing anything.

_Note2_: jQuery is used only for DOM manipulation purpose, it's not required at all.

_Note3_: On the other side, sockjs framework IS needed.

As this is an example, the ```notification.js``` and ```socket.js``` can be reused without modification into your application, they are both framework-less (except SockJS). The last file ```action.js``` is this time specific to this demonstration.


## Socket.js

A simple layer for sockjsroom, this helps to use the multi-message capacities. It can be reused like this for every project you may have (the same file can be reused for all sockjsroom application).


## Notification.js

A layer for implementing API provided by server, this should remains the same for your own application, it's not needed to change it.


## Action.js

This file is specific to this example, in this file you will find how to catch websocket event, and apply them.

Basically, a socket event (from ```notification.js```), will send on every example an object:
```js

// Bind to all notifications arriving
notification.bind(function(details) {
    // You can access to :
    details.element; // The given element (system send them one by one)
    details.event; // The server event: seen, delete, notification
    details.seen; // Number of 'seen' notification currently stored on client side
    details.unseen; // Number of 'unseen' notification (the most interesting)
    details.all; // Number of notifications
});

// Bind to only 'message' notification
notification.bind('message', function(details) {

});
```

What is important here, is the difference between two binding:
  - Message will only take care of notification with the 'message' type. Others notifications will be ignored. This means that details.seen, details.unseen, and details.all, would be restricted to others type 'message'.

This means you don't need to count how much items exist for every type, system will do it for you.

The main example, will be of course, facebook: you can have default notification (somebody type something into your wall/reply to you), and message notification (somebody sent you a message).
You don't want to count all of them, only how many message unseen, and how many 'others' unseen exist. This behavior is implented by default here threw this process.

