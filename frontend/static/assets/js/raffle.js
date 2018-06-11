window.cgsy = window.cgsy || {};
window.cgsy.raffle = window.cgsy.raffle || {};

(function($, raffle) {
    "use strict";

    var subscriptions = [];

    raffle.Raffle = function() {
        var deleteSubscription = function(id) {
            var subs = [];
            $.each(subscriptions, function(id, sub) {
                if (sub.id !== id) {
                    subs.push(sub);
                }
            });
            subscriptions = subs;
        };

        this.addSubscriber = function(id, name) {
            subscriptions.push({
                'id': id,
                'name': name
            });
        };
        
        this.run = function (target_el, sub_id_el, callback) {
            target_el = $(target_el);
            sub_id_el = $(sub_id_el);
            if (!subscriptions.length) {
                alert('Nenhuma inscrição registrada.');
                return;
            }
            var selected = subscriptions[
                Math.floor(Math.random() * subscriptions.length)
            ];
            sub_id_el.val(selected.id);
            deleteSubscription(selected.id);
            target_el.text(selected.name);

            if (callback) {
                callback();
            }
        }
    };

})(jQuery, window.cgsy.raffle);


(function($, AjaxSender, raffle) {
    "use strict";

    raffle.Winners = function() {
        this.register = function(url, target_el, subscription_pk, callback) {
            target_el = $(target_el);
            var sender = new AjaxSender(url);
                sender.setSuccessCallback(function(response) {
                    target_el.html(response);
                    if (callback) {
                        callback(response);
                    }
                });
                sender.send('POST', {
                    'subscription': subscription_pk
                });
        };

        this.render = function(url, target_el) {
            target_el = $(target_el);
            var sender = new AjaxSender(url);
                sender.setSuccessCallback(function(response) {
                    target_el.html(response);
                });
                sender.send('GET');
        };
    };
})(jQuery, window.cgsy.AjaxSender, window.cgsy.raffle);