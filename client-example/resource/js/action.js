/**
 * Create a new socket instance and try to connect to it
 *
 * @method doLogin
*/
function doLogin() {
    var login = $('#signin #login').val(),
        password = $('#signin #password').val();

    if(login && password && login != '' && password != '') {
        notification.connect(login, CryptoJS.SHA512(password).toString());

        // We hide previous element and show new one
        $('#hide-after-login, #signin').hide();
        $('#hide-before-login, #signout').show();

        // Some notification are now marked as 'seen'
        notification.bind(function(details) {
            console.log('recieve events');
            console.log(details);

            if(details.event === 'notification') {
                var notification = details.element,
                    seen = notification.seen;

                var container = $('#single-notification > div').clone();
                container.find('h4').html(notification.title);
                container.find('p').html(notification.content);
                container.find('button').data('objid', notification['_id']);

                // Empty or not valid url
                if(!notification.url) {
                    container.find('a.link').css('display', 'none');
                } else {
                    container.find('a.link').attr('href', notification.url);
                }

                if(seen == 'false' || seen == false) {
                    container.addClass('unseen-notification');
                } else {
                    container.addClass('seen-notification');
                }

                $('#content-show').append(container);
            }
        });
    }
};



/**
 * Logout, destroy and stop socket.
 *
 * @method doLogout
*/
function doLogout() {
    doClear();
    notification.unbindAll();
    notification.disconnect();
    $('#hide-before-login, #signout').hide();
    $('#hide-after-login, #signin').show();
};


/**
 * Clear existing content
 *
 * @method doClear
*/
function doClear() {
    $('#content-show').html('');
};


/**
 * Ask to get more notifications
 *
 * @method doContent
*/
function doContent() {
    notification.content(0);
};


/**
 * Get the unseen element
 *
 * @method doUnseen
*/
function doUnseen() {
    notification.unseen();
};

/**
 * Mark given id as seen
 *
 * @method doSeen
*/
function doSeen(el) {
    var id = $(el).data('objid');
    notification.seen([id]);
};

/**
 * Create a new notification for one or more users
 *
 * @method doNotify
*/
function doNotify() {
    // Send ajax request
    $.post('//' + window.location.hostname + ':8587/notify',
        $('form#notify').serialize(), function(data) {}
    );
};