window.cgsy = window.cgsy || {};
window.cgsy.messenger = window.cgsy.messenger || {};

(function (Messenger, messenger) {
    "use strict";

    Messenger.options = {
        extraClasses: 'messenger-fixed messenger-on-bottom ' +
            'messenger-on-right',
        theme: 'flat'
    };

    messenger.triggerEvent = function (type, msg, id) {
        var data = {
            type: type,
            message: msg,
            showCloseButton: true,
            hideAfter: 10
        };
        if (id) {
            data['id'] = id;
        }
        return Messenger().post(data);
    };

    messenger.triggerSuccess = function (msg, id) {
        return cgsy.messenger.triggerEvent('success', msg, id);
    };

    messenger.triggerWarning = function (msg, id) {
        return cgsy.messenger.triggerEvent('warning', msg, id);
    };

    messenger.triggerInfo = function (msg, id) {
        return cgsy.messenger.triggerEvent('info', msg, id);
    };

    messenger.triggerError = function (msg, id) {
        return cgsy.messenger.triggerEvent('error', msg, id);
    };

    messenger.triggerLoader = function (msg, id) {
        return Messenger().run({
            hideAfter: 50000, // long time. Loader will wait to be finished.
            progressMessage: msg,
            id: id,
            action: function () {} // action will persist notification.
        });
    };

    messenger.retry = function (messenger_instance, handler, msg) {
        messenger_instance.update({
            message: msg,
            type: 'error',
            actions: {
                retry: {
                    label: 'Tentar novamente',
                    phrase: 'Retrying TIME',
                    auto: true,
                    delay: 10,
                    action: function () {
                        handler();
                        messenger_instance.cancel();
                    }
                }
            }
        });
    };

    messenger.update = function (messenger_instance, type, msg, seconds) {
        messenger_instance.update({
            type: type,
            message: msg,
            hideAfter: seconds || 10,
            showCloseButton: true
        });
    };

    messenger.close = function (messenger_instance) {
        messenger_instance.hide();
    };

    messenger.closeAll = function() {
        Messenger().hideAll();
    };

})(Messenger, window.cgsy.messenger);