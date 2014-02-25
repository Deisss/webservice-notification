# webservice-notification

A server to plug into your own system, to create a notification system between some server side event, and your users. This aims to provide something close to what you can found on facebook (for example), with a small footprint on your existing server architecture and client.



## Installation

As it is a real system, get some time before starting (around 10/15min should be enough), here is the list of programs we need:

  * MongoDB
  * Python (with few packages)
  * MySQL (see below)

The system is using MongoDB as a primary database, and MySQL is here to show an example how to plug your logic (security) to this system (we will explain later).

**The installation is describe for CentOS/RedHat system**



### Database
We need only MongoDB:

```
yum -y install mongodb
```

For mongodb you may need to use [MongoDB](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/) repository instead of default one.

That will be enough, of course if you want to run MySQL example, you will need also MySQL setup (package **mysql** and **mysql-server**).



### Python
The main development is based on Python 2.x branch, but should work like a charm on Python 3.x branch. We need to install python and few dependencies:

```
yum -y install \
    python python-devel \
    python-setuptools python-pip \
    MySQL-python
```



### PIP
Now we have a Python instance ready and running, we need additional packages:
```
pip install tornado pymongo sockjs-tornado sockjsroom PyDispatcher
```

We install:
  * **tornado, sockjs-tornado, sockjsroom**: packages to manage server system, and real time server system,
  * **pymongo**: use MongoDB into python,
  * **PyDispatcher**: a PubSub system used between new notification, and currently connected user.

 
Now we have the full system installed, we miss to clone this repository:
```
mkdir ws_notification
cd ws_notification
git clone https://github.com/Deisss/webservice-notification.git .
```

We are ready to configure.




## Configure

Before doing anything else, it's quite recommended (required in fact) to setup configuration; from ```ws_notification```, go into ```server``` directory, and edit ```config.ini```:
```
cd ws_notification/server
vim config.ini
```
For every category (except APPLICATION), you have a DEBUG and RELEASE element, you should configure every part according to your own server configuration. All of them are 'classical' configuration, like email provider, database host, so we don't explain them here...

Now we can start system.




## Usage

First of all, you need to launch the server. from ```ws_notification```, go into ```server``` directory, open a command prompt and type ```python server.py```:
```
python server.py
```
That's enough, no need to do more to have server ready. Now we will explain API available (quite simple).




## API - server

Server(s) can send new notifications threw a single URL:
  * **POST** => **/notify**:
      - *type* | string: The notification type
      - *title* | string: The notification title
      - *content* | string: The notification content
      - *url* | string: The associated url
      - *icon* | string: A field to set icon
      - *image* | string: An image (like gravatar image)
      - *users* | string (json doc): A list of users who are concerned by this notification (see below)

**/!\ Except content, all elements are not required. This is simply due to the fact that server doesn't do anything with! The client may use some or all of them (you decide). Basically this server only make relation between notification and user, so it doesn't use them at all, only store them...**

**/!\ Remember also that users are important: if you specify none of them, nothing will happend/be done... As the server create one notification for one user in database.**

The **users** parameter is the most important here, it's a simple JSON document (in string format) indicating who is concerned by this notification, let's show an example as it's quite easy:
```
[
    {
        "id": 1,
        "email": "myemail@test.com"
    },
    {
        "id": 2,
        "email": "second@test.com"
    }
]
```
Will try to find user with id 1 and 2 into websocket system (=currently connected), if at least, one of them is not found, it will use the related email to send an email instead (see below).


Those elements represent a notification in most of existings system. But this system is able to do little more, so we provide extra parameters:
  * **email_send**: a boolean indicate is system should send an email if one or more user is not currently connected to websocket system (=not online)
  * **email_force**: no matter if user is connected or not, they should ALL recieve email notification
  * **email_subject**: A subject for the email
  * **email_content**: The email content
  * **email_mime** (default: 1.0): email MIME Version
  * **email_type** (default: text/html): The content type of the email

*Note*: if email_send is not activated, system will never send email, so you need this parameter if you want to use email service.

*Note2*: only one email is sent, with everybody in BCC.


This is the only entry point for sending notification to system. Of course this point should not be accessible from outside, only from your local server.

**/!\ Please keep in mind that this server does not provide ANY security check regarding what is sent to user. It means content, title and others fields are not escaped or checked against any traditionnal security trouble, you should take a lot care about this BEFORE sending to this system any content.**



## API - client

Now we know how to deal with adding new notification, it remains the client side: how user get new notification, and how you can use them.

The client API is only composed with a single websocket, so the whole API is based on that. Moreover, we use on top of [SockJS](https://github.com/mrjoes/sockjs-tornado), [sockjsroom](https://github.com/Deisss/python-sockjsroom) for creating multi-message system.
As websocket is bi-directionnal, we separate them:

**From client to server:**
  * **unseen**: get the unseen notifications for the given user. It should not be so much needed, as everytime user connect to socket, you get exactly this return. Take no parameter.
  * **content**: get page by page existing notifications (no matter they are unseen or not). Take page (integer) as parameter.
  * **seen**: mark some notification as seen. Take an array of ObjectId's as parameter (the *_id* field from every notification you want to mark as seen).
  * **delete**: mark some notification as deleted. Take an array of ObjectId's as parameter (the *_id* field from every notification you want to mark as delete).

We strongly recommand you to check the example provided to have a working base to modify, and also check how to use those elements.

**From server to client:**
  * **notification**: The server send some new notification, or send back data requested by user (like _unseen_ and _content_)
  * **seen**: Some notification have been marked as 'seen', we should apply modification...
  * **delete**: Some notification have been marked as 'deleted', we should remove them...

The notification is highly used by most of functions.
From this API, now the client has to deal with information given, the seen and delete state should be enough to control the notification lifetime.
