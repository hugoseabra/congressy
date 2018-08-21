window.cgsy = window.cgsy || {};
window.cgsy.messenger = window.cgsy.messenger || {};

(function (Messenger, cgsy) {
    "use strict";

    Messenger.options = {
        extraClasses: 'messenger-fixed messenger-on-bottom ' +
        'messenger-on-right',
        theme: 'flat'
    };

    var messenger = {};

    messenger.triggerEvent = function (type, msg) {
        Messenger().post({
            type: type,
            message: msg
        });
    };

    messenger.triggerSuccess = function (msg) {
        cgsy.messenger.triggerEvent('success', msg);
    };

    messenger.triggerWarning = function (msg) {
        cgsy.messenger.triggerEvent('warning', msg);
    };

    messenger.triggerError = function (msg) {
        cgsy.messenger.triggerEvent('error', msg);
    };

    cgsy.messenger = messenger;
})(Messenger, window.cgsy);