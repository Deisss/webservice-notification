/**
 * A notification system for grabbing important event threw the user session
 * lifetime
 *
 * @class notification
 * @static
*/
var notification = {
    /**
     * Store the created socket instance
     * @property _socket
     * @type Object
     * @default null
    */
    _socket: null,

    /**
     * Store the 'all' type element
     * @property _allType
     * @type String
     * @default __all__
    */
    _allType: '__all__',

    /**
     * Keep a trace of all 'unseen' notifications
     * @property _unseen
     * @type Object
     * @default {}
    */
    _unseen: {},

    /**
     * Keep a trace of all notifications (include unseen)
     * @property _all
     * @type Object
     * @default {}
    */
    _all: {},

    /**
     * Store binded function when recieving something
     * @property _bind
     * @type Object
     * @default {}
    */
    _bind: {},


    /**
     * Get the object size (kind of length)
     *
     * @method _getObjectSize
     *
     * @param obj {Object}                  The object to check
     * @return {Integer}                    The count found
    */
    _getObjectSize: function(obj) {
        if(!obj) {
            return 0;
        }
        var key, count = 0;
        for(key in obj) {
            if(obj.hasOwnProperty(key)) {
                count++;
            }
        }
        return count;
    },


    /**
     * Raise a new event
     *
     * @method _raiseEvent
     * @private
     *
     * @param type {String}                 The notification type, or all
     * @param name {String}                 The event type (like 'seen',
     *                                      'delete')
     * @param el {Object}                   The concerned notification
    */
    _raiseEvent: function(type, name, el) {
        type = type || this._allType;

        if(this._bind[type]) {
            var tab = this._bind[type],
                i = tab.length;

            var unseenLength = 0,
                allLength    = 0,
                seenLength   = 0;

            // We select length globally
            if(type == this._allType) {
                unseenLength = this._getObjectSize(this._unseen);
                allLength = this._getObjectSize(this._all);

            // We select only the sub-length of some elements
            } else {
                var g = this._getObjectSize(this._all);

                while(g--) {
                    var notification = this._all[g];
                    if(notification['type'] === type) {
                        var seen = notification['seen'];
                        allLength++;

                        if(seen == false || seen == 'false' || seen == 'unseen'
                            || seen == '0' || seen == 0) {
                            unseenLength++;
                        }
                    }
                }
            }

            // The seenLength is always the same...
            seenLength = allLength - unseenLength;

            while(i--) {
                var fct = tab[i];
                // Send the event
                setTimeout(function() {
                    fct({
                        event:   name,
                        element: el,
                        seen:    seenLength,
                        unseen:  unseenLength,
                        all:     allLength,
                    });
                }, 0);
            }
        }
    },

    /**
     * Start the notification system.
     *
     * @method connect
     *
     * @param login {String}                The login to use
     *                                      (same as global system)
     * @param password {String}             The password to use
     *                                      (same as global system => sha512)
     * @return {Object}                     The socket instance created
    */
    connect: function(login, password) {
        var instance = new socket('notification');

        // On every connect, the server 'loose' us
        // so we have to join again
        instance.on('connect', function() {
            // Everytime a connect appear, we have to logon again
            this.emit('join', {
                login: login,
                password: password
            });
        }, instance);

        // On seen, we remove from unseen only
        instance.on('seen', function(ids) {
            var elements = [];

            // Some element has been marked as seen
            for(var i=0, l=ids.length; i<l; ++i) {
                var id = ids[i];

                // We raise a new event
                if(this._unseen[id]) {
                    elements.push(this._unseen[id]);
                    delete this._unseen[id];
                }
            }

            for(var i=0, l=elements.length; i<l; ++i) {
                var element = elements[i];

                if(element) {
                    if(element['type']) {
                        this._raiseEvent(element['type'], 'seen', element);
                    }

                    this._raiseEvent(null, 'seen', element);
                }
            }
        }, this);

        // On delete, we try to remove elements existing inside
        instance.on('delete', function(ids) {
            var elements = [];

            for(var i=0, l=ids.length; i<l; ++i) {
                var id = ids[i];
                if(this._all[id]) {
                    elements.push(this._all[id]);

                    delete this._unseen[id];
                    delete this._all[id];
                }
            }

            for(var i=0, l=elements.length; i<l; ++i) {
                var element = elements[i];

                if(element) {
                    if(element['type']) {
                        this._raiseEvent(element['type'], 'delete', element);
                    }

                    this._raiseEvent(null, 'delete', element);
                }
            }
        }, this);

        // On notification, we erase previous content or append
        instance.on('notification', function(notifications) {
            var elements = [];

            for(var i=0, l=notifications.length; i<l; ++i) {
                var notification = notifications[i],
                    id   = notification['_id'],
                    seen = notification['seen'];

                elements.push(notification);

                // We try to append
                if(seen == false || seen == 'false' || seen == 'unseen'
                    || seen == '0' || seen == 0) {
                    this._unseen[id] = notification;
                }
                this._all[id] = notification;
            }

            for(var i=0, l=elements.length; i<l; ++i) {
                var element = elements[i];

                if(element) {
                    if(element['type']) {
                        this._raiseEvent(element['type'],
                                        'notification', element);
                    }

                    this._raiseEvent(null, 'notification', element);
                }
            }
        }, this);

        // Start socket
        instance.connect();

        this._socket = instance;
        return instance;
    },

    /**
     * Mark as seen some ids.
     *
     * @method seen
     *
     * @param ids {Array}                   An array of ObjectId (string way)
     *                                      to mark as seen
    */
    seen: function(ids) {
        if(this._socket !== null) {
            this._socket.emit('seen', {
                ids: ids
            });
        }
    },

    /**
     * Grab the unseen notifications from server (should not be needed at all)
     * As when user connect, it automatically retrieve unseen notifications...
     *
     * @method unseen
    */
    unseen: function() {
        if(this._socket !== null) {
            this._socket.emit('unseen', {});
        }
    },

    /**
     * Mark as deleted selected ids
     *
     * @method delete
     *
     * @param ids {Array}                   An array of ObjectId (string way)
     *                                      to mark as deleted
    */
    delete: function(ids) {
        if(this._socket !== null) {
            this._socket.emit('delete', {
                ids: ids
            });
        }
    },

    /**
     * Ask the server to bring some existing content (page by page)
     *
     * @method content
     *
     * @param page {Integer}                The page to recieve
    */
    content: function(page) {
        if(this._socket !== null) {
            this._socket.emit('content', {
                page: Math.min(0, page)
            });
        }
    },

    /**
     * Stop the notification system.
     *
     * @method disconnect
    */
    disconnect: function() {
        if(this._socket !== null) {
            this._socket.disconnect();
            this._socket = null;
        }
    },

    /**
     * Bind a function to a new notification arriving (regarding the type).
     * If you don't put any type to this function, the function will be binded
     * to all elements recieve.
     *
     * @method bind
     *
     * @param type {String}                 The notification type to bind
     * @param fct {Function}                The function to respond in case of
     *                                      new element arriving
    */
    bind: function(type, fct) {
        var f = 'function';

        if(typeof(type) === f) {
            fct = type;
            type = this._allType;
        }

        if(!this._bind[type]) {
            this._bind[type] = [];
        }

        if(typeof(fct) === f) {
            this._bind[type].push(fct);
        }
    },

    /**
     * Remove from binding a function previously binded using bind.
     * Like bind, if you specify only a function as parameter, the 'all' type
     * will be remove.
     *
     * @method unbind
     *
     * @param type {String}                 The notification type to bind
     * @param fct {Function}                The function to remove
    */
    unbind: function(type, fct) {
        if(typeof(type) === 'function') {
            fct = type;
            type = this._allType;
        }

        if(this._bind[type]) {
            var tab = this._bind[type],
                l = tab.length;

            while(l--) {
                if(tab[l] === fct) {
                    tab.splice(l, 1);
                }
            }

            if(tab.length == 0) {
                this.unbindAll(type);
            }
        }
    },

    /**
     * Remove all functions binded to a given type.
     * You can not specify type to unbind on 'all' type
     *
     * @method unbindAll
     *
     * @param type {String}                 The notification type to clear
    */
    unbindAll: function(type) {
        if(!type) {
            type = this._allType;
        }
        delete this._bind[type]; 
    }
};