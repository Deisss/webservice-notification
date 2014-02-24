/**
 * Create a new SockJS instance.
 *
 * @class socket
 * @constructor
 *
 * @param namespace {String | null} The namespace to link SockJS with
*/
var socket = function(namespace) {
    // Store events list
    this.events    = {};
    // The base url
    this.url       = '//' + window.location.hostname;
    // The base port
    this.port      = 8587;
    // Store the SockJS instance
    this.instance  = null;
    // Store the namespace
    this.namespace = namespace || '';
    // Should reconnect or not
    this.reconnect = true;
};



socket.prototype = {
    /**
     * Bind a function to an event from server.
     *
     * @method on
     *
     * @param name {String}                 The message type
     * @param fct {Function}                The function to call
     * @param scope {Object | null}         The scope to apply for function
    */
    on: function(name, fct, scope) {
        var fn = fct;
        if(scope) {
            // We bind scope
            fn = function() {
                fct.apply(scope, arguments);
            };
        }
        // If it's not existing, we create
        if(!this.events[name]) {
            this.events[name] = [];
        }
        // Append event
        this.events[name].push(fn);
    },

    /**
     * Send data to server.
     *
     * @method emit
     *
     * @param name {String}                 The message type
     * @param data {Object}                 The linked data with message
    */
    emit: function(name, data) {
        this.instance.send(
            JSON.stringify({
                name: name,
                data: data
            })
        );
    },

    /**
     * Connect to server.
     *
     * @method connect
    */
    connect: function() {
        // Disconnect previous instance
        if(this.instance) {
            // Get auto-reconnect and re-setup
            var p = this.reconnect;
            this.disconnect();
            this.reconnect = p;
        }

        // Start new instance
        var base = (this.port != 80) ? this.url + ':' + this.port : this.url;
        var sckt = new SockJS(base + '/' + this.namespace, null, {
            debug : false,
            devel : false
        });

        var _this = this;

        /**
         * Parse event from server side, and dispatch it
         *
         * @method catchEvent
         *
         * @param response {Object}         The data from server side
        */
        function catchEvent(response) {
            var name   = (response.type) ? response.data.name : response.name,
                data   = (response.type) ? response.data.data : response.data,
                evts   = _this.events[name];
            if(evts) {
                var parsed = (typeof(data) === 'object' && data !== null) ?
                            data : JSON.parse(data);

                for(var i=0, l=evts.length; i<l; ++i) {
                    var fct = evts[i];
                    if(typeof(fct) === 'function') {
                        // Defer call on setTimeout
                        (function(f) {
                            setTimeout(function() {f(parsed);}, 0);
                        })(fct);
                    }
                }
            }
        };

        // Catch open
        sckt.onopen = function() {
            catchEvent({
                name: 'open',
                data: {}
            });
            catchEvent({
                name: 'connect',
                data: {}
            });
        };

        // Catch arriving message
        sckt.onmessage = function(data) {
            catchEvent(data);
        };

        // Catch close, and reconnect
        sckt.onclose = function() {
            catchEvent({
                name: 'close',
                data: {}
            });
            catchEvent({
                name: 'disconnect',
                data : {}
            });
            if(_this.reconnect) {
                _this.connect();
            }
        };

        // Link to server
        this.instance = sckt;
    },

    /**
     * Disconnect from server.
     *
     * @method disconnect
    */
    disconnect: function() {
        this.reconnect = false;

        if(!this.instance) {
            return;
        }

        this.instance.close();
        this.instance = null;
    }
};