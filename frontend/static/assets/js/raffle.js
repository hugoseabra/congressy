window.cgsy = window.cgsy || {};
window.cgsy.raffle = window.cgsy.raffle || {};

(function($, raffle) {
    "use strict";

    var subscriptions = [];
    var winners = [];

    raffle.Raffle = function() {

        var self = this;
        var winner_out = true;

        var deleteSubscription = function(id) {
            var subs = [];
            $.each(subscriptions, function(i, sub) {
                if (sub.id !== id) {
                    subs.push(sub);
                }
            });
            subscriptions = subs;
        };

        this.shuffleAll = function() {
            winner_out = false;
        };

        this.addSubscriber = function(id, name) {
            subscriptions.push({
                'id': id,
                'name': name
            });
        };

        this.registerWinner = function(sub_id) {
            console.log('winner: ' + sub_id);
            winners.push(sub_id)
        };

        this.unregisterWinner = function(sub_id) {
            console.log('winner unregistered: ' + sub_id);
            var winners2 = [];
            $.each(winners, function(i, winner) {
                if (winner !== sub_id) {
                    winners2.push(winner);
                }
            });
            winners = winners2;
        };
        
        this.run = function (target_el, sub_id_el, counter_el) {
            target_el = $(target_el);
            sub_id_el = $(sub_id_el);

            var num = subscriptions.length - winners.length;
            console.log(subscriptions);
            console.log(winners);

            if (counter_el) {
                $(counter_el).text(num);
            }

            target_el.removeClass('text-success text-bold');

            if (!num) {
                alert('Nenhuma inscrição a ser sorteada.');
                return new Promise(function(resolve) { resolve(); });
            }

            // normalize
            num = num - 1;
            var shuffle_interval = 50;

            return new Promise(function(resolve) {
                $.each(subscriptions, function(i, sub) {
                    console.log(sub);
                    window.setTimeout(function() {
                        target_el.text(sub.name);
                    }, i * shuffle_interval);

                    if (i === num) {
                        window.setTimeout(function() {
                            target_el.text('processando ...');
                        }, i * (shuffle_interval + 100));

                        window.setTimeout(function() {
                            var selected = self.select();
                            sub_id_el.val(selected.id);
                            target_el.text(selected.name);
                            target_el.addClass('text-success text-bold');

                            resolve(selected);
                        }, (i * 2) * (shuffle_interval + 200));
                    }
                });
            });
        };

        this.select = function() {
            var id = Math.floor(Math.random() * subscriptions.length);

            var is_winner = $.inArray(id, winners) !== -1;
            if (is_winner && winner_out === true) {
                return this.select();
            }

            return subscriptions[id];
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

        this.delete = function(url, sub_k) {
            return new Promise(function(resolve) {
                var sender = new AjaxSender(url);
                    sender.setSuccessCallback(function(response) {
                        resolve(response)
                    });
                    sender.send('POST', {'pk': sub_k});
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