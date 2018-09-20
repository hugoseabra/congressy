/**
 * CGSY ATTENDANCE
 *
 * Biblioteca para gerenciar check-in/out de participantes de um evento.
 *
 * CRITÉRIOS:
 * ----------
 *
 * O check-in/ou acontece mediante os seguintes critérios:
 * - participantes sempre terá um status: confirmado, aguardando, cancelado;
 * - somente participantes confirmados poderão ser confirmados no evento, ou
 *   seja, ter o seu check-in realizado;
 * - participantes com status "aguardando" e "cancelados" devem ter essa
 *   informação explícita durante o processo de check-in/ou;
 * - o processo de check-in/out será sempre realizado por meio de um
 *   Atendimento;
 * - Um Atendimento poderá ter filtros diversos:
 *      - categoria de participantes;*
 * - o processo de check-in/out será realizado através de busca dos
 *   participantes confirmados, pelos seguintes meios:
 *      - busca manual (digitada) com critérios abertos, com resultados
 *        diversos, com confirmação (entrada/saída) através de um clique do
 *        mouse;
 *      - busca por meio de um leitor de código de barras, com resultado único
 *        e confirmação (entrada/saída) através da re-leitura do código do
 *        barras (podendo também ser feito pelo mouse);
 *        - busca por meio de um leitor de QRCode, com resultado único e
 *          confirmação (entrada/saída) através da re-leitura do QR Code
 *          (podendo também ser feito pelo mouse);
 *
 * ARQUITETURA:
 * ------------
 *
 * Precisamos das seguintes inteligências para suprir os critérios:
 * - cgsy.attendance.Attendance:
 *      - identificação do Atendimento do contexto;
 *      - Endpoint URI de check-in;
 *      - Endpoint URI de check-out;
 *      - Callbacks de check-in;
 *      - Callbacks de check-out;
 *
 * - cgsy.attendance.Card:
 *      - dados de inscrição;
 *      - cgsy.attendance.Attendance;
 *      - histórico de check-in/out;
 *
 * - cgsy.attendance.CardList;
 *
 * - cgsy.attendance.KeyboardSearch:
 *      - cgsy.attendance.CardList;
 *      - Endpoint URI de busca de inscrições;
 *
 * - cgsy.attendance.BarcodeSearch;
 *      - Endpoint URI de busca de inscrições;
 *
 * - cgsy.attendance.QRCodeSearch;
 *      - Endpoint URI de busca de inscrições;
 *
 */
window.cgsy = window.cgsy || {};
window.cgsy.attendance = window.cgsy.attendance || {};

// ==========================================================================//
// SUBSCRIPTION
// ==========================================================================//
(function (AjaxSender, attendance) {
    attendance.Subscription = function (uuid,
                                        name,
                                        lot_name,
                                        category_name,
                                        email,
                                        event_count,
                                        code,
                                        subscription_status,
                                        attendance_status) {
        var self = this;
        this.uuid = uuid;
        this.name = name.substring(0, 22);
        this.lot_name = lot_name.substring(0, 30);
        this.category_name = category_name.substring(0, 30);
        this.email = email.substring(0, 30);
        this.event_count = event_count;
        this.code = code;
        this.subscription_status = subscription_status;
        this.attendance_status = attendance_status;

        this.checkins = [];

        var subscription_uri = null;

        this.setUri = function (uri) {
            subscription_uri = uri;
        };

        this.fetch = function (service_pk) {
            if (!uuid) {
                console.error('No UUID provided to fetch subscription.');
                return;
            }
            if (!subscription_uri) {
                console.error('No Endpoint URI to fetch subscription.');
                return;
            }
            if (!service_pk) {
                console.error('No attendance service pk to fetch subscription.');
                return;
            }

            subscription_uri = subscription_uri.replace(':pk', uuid);

            return new Promise(function (resolve) {

                var sender = new AjaxSender(subscription_uri);
                sender.setSuccessCallback(function (response) {
                    console.log('1. Fetch - status anterior: ' + response['attendance_status']);

                    self.name = response['person']['name'].substring(0, 22);
                    self.lot_name = response['lot']['name'].substring(0, 30);
                    if (response['lot']['category']) {
                        self.category_name = response['lot']['category'].substring(0, 30);
                    }
                    self.email = response['person']['email'].substring(0, 30);
                    self.event_count = response['event_count'];
                    self.code = response['code'];
                    self.subscription_status = response['status'];
                    self.attendance_status = response['attendance_status'];

                    self.checkins = [];
                    var incoming_checkins = response['checkins'];
                    if (incoming_checkins.length) {
                        $.each(incoming_checkins, function (i, item) {
                            var checkout = item['checkout'];

                            self.addCheckinNote(
                                item['id'],
                                item['created_by'],
                                item['created_on'],
                                checkout ? item['checkout']['created_by'] : null,
                                checkout ? item['checkout']['created_on'] : null
                            )
                        });
                    }

                    resolve();
                });
                sender.send('GET');
            });
        };

        this.addCheckinNote = function (pk,
                                        checkin_by,
                                        checkin_on,
                                        checkout_by,
                                        checkout_on) {
            var data = {
                'pk': pk,
                'checkin_by': checkin_by,
                'checkin_on': checkin_on,
                'checkout_by': null,
                'checkout_on': null
            };

            if (checkout_by && checkout_on) {
                data['checkout_by'] = checkout_by;
                data['checkout_on'] = checkout_on;
            }

            this.checkins.push(data);
        };
    };

})(window.cgsy.AjaxSender, window.cgsy.attendance);

// ==========================================================================//
// SUBSCRIPTION COLLECTION
// ==========================================================================//

(function (AjaxSender, Subscription, attendance) {

    attendance.SubscriptionCollection = function (collection_uri) {

        var self = this;
        this.subscriptions = [];
        var subscription_uri = collection_uri + ':pk/';

        var createSubscription = function (data) {
            var subscription = new Subscription(
                data['uuid'],
                data['person']['name'],
                data['lot']['name'],
                data['lot']['category'],
                data['person']['email'],
                data['event_count'],
                data['code'],
                data['status'],
                data['attendance_status']
            );
            subscription.setUri(subscription_uri);

            var incoming_checkins = data['checkins'];
            if (incoming_checkins.length) {
                $.each(incoming_checkins, function (i, item) {
                    var checkout = item['checkout'];

                    subscription.addCheckinNote(
                        item['id'],
                        item['created_by'],
                        item['created_on'],
                        checkout ? checkout['created_on'] : null,
                        checkout ? checkout['created_by'] : null
                    );
                });
            }

            return subscription;
        };

        this.fetch = function (search_criteria) {
            this.subscriptions = [];

            return new Promise(function (resolve) {
                var uri = collection_uri + '?page=1&search=' + search_criteria;
                var sender = new AjaxSender(uri);
                sender.setSuccessCallback(function (response) {
                    if (response.results.length === 0) {
                        return;
                    }
                    $.each(response.results, function (i, item) {
                        self.subscriptions.push(createSubscription(item));
                    });
                    resolve(self.subscriptions);
                });
                sender.get();
            });
        };
    };

})(window.cgsy.AjaxSender, window.cgsy.attendance.Subscription, window.cgsy.attendance);

// ==========================================================================//
// ATTENDANCE
// ==========================================================================//
(function (AjaxSender, attendance) {

    attendance.Attendance = function (checkin_uri, success_checkin_msg,
                                      fail_checkin_msg, checkout_uri,
                                      success_checkout_msg, fail_checkout_msg) {

        var preCheckinCallbacks = [];
        var postCheckinCallbacks = [];
        var preCheckoutCallbacks = [];
        var postCheckoutCallbacks = [];

        this.addPreCheckinCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            preCheckinCallbacks.push(callback);
        };

        this.addPostCheckinCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            postCheckinCallbacks.push(callback);
        };

        this.addPreCheckoutCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            preCheckoutCallbacks.push(callback);
        };

        this.addPostCheckoutCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            postCheckoutCallbacks.push(callback);
        };

        this.checkin = function (service_pk, subscription, created_by) {
            return new Promise(function (resolve) {
                if (!checkin_uri) {
                    alert('You must provide checkin endpoint URI.');
                    return;
                }

                subscription.fetch(service_pk).then(function () {

                    var sender = new AjaxSender(checkin_uri);
                    sender.setBeforeSendCallback(function () {
                        $.each(preCheckinCallbacks, function (i, callback) {
                            callback();
                        });
                    });
                    sender.setSuccessCallback(function (response) {
                        $.each(postCheckinCallbacks, function (i, callback) {
                            callback();
                        });
                        console.log('2. checkin realizado.');
                        Messenger().post({
                            message: success_checkin_msg,
                            type: 'success'
                        });
                        subscription.fetch(service_pk, created_by).then(function () {
                            resolve();
                        });
                    });
                    sender.setFailCallback(function () {
                        Messenger().post({
                            message: fail_checkin_msg,
                            type: 'error'
                        });
                    });

                    sender.post({
                        'subscription': subscription.uuid,
                        'attendance_service': service_pk,
                        'created_by': created_by
                    });
                });
            });
        };

        this.checkout = function (service_pk, subscription, created_by) {
            return new Promise(function (resolve) {
                if (!checkout_uri) {
                    alert('You must provide checkout endpoint URI.');
                    return;
                }

                if (!checkin_uri) {
                    alert('You must provide checkin endpoint URI.');
                    return;
                }

                subscription.fetch(service_pk).then(function () {

                    var checkins = subscription.checkins;
                    if (checkins.length === 0) {
                        alert('Subscription is not attended in this service.');
                        return;
                    }
                    var last_checkin = checkins[checkins.length - 1];


                    var sender = new AjaxSender(checkout_uri);
                    sender.setBeforeSendCallback(function () {
                        $.each(preCheckoutCallbacks, function (i, callback) {
                            callback();
                        });
                    });
                    sender.setSuccessCallback(function (response) {
                        $.each(postCheckoutCallbacks, function (i, callback) {
                            callback();
                        });
                        Messenger().post({
                            message: success_checkout_msg,
                            type: 'success'
                        });
                        subscription.fetch(service_pk, created_by).then(function () {
                            resolve();
                        });
                    });

                    sender.setFailCallback(function () {
                        Messenger().post({
                            message: fail_checkout_msg,
                            type: 'error'
                        });
                    });
                    sender.post({
                        'checkin': last_checkin['pk'],
                        'created_by': created_by
                    });
                });
            });
        };
    };

})(window.cgsy.AjaxSender, window.cgsy.attendance);

// ==========================================================================//
// CARD
// ==========================================================================//
(function ($, attendance) {

    /**
     * @param {Subscription} subscription
     * @param {Attendance} attendance
     * @constructor
     */
    attendance.Card = function (subscription, attendance) {

        var self = this;
        var card_parent_el = null;
        var card_el = null;
        var card_size = 4;
        var toggleStateCallbacks = [];
        var toggleCallbacksInit = false;

        const STATUS_PENDING = 'awaiting';
        const STATUS_CANCELLED = 'canceled';
        const STATUS_CHECKED = 'checked';
        const STATUS_NOT_CHECKED = 'not-checked';

        const COLOR_PENDING = '#EDCE8C';
        const COLOR_DISABLED = '#e25d5d';
        const COLOR_NOT_CHECKED = '#909AA0';
        const COLOR_CHECKED = '#27B6AF';

        this.subscription = subscription;

        this.addToggleStateCallback = function (callback) {

            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            toggleStateCallbacks.push(callback);
        };

        var getStatus = function () {
            if (subscription.subscription_status === 'confirmed') {
                var is_checked = subscription.attendance_status === true;
                if (is_checked) {
                    return STATUS_CHECKED;
                }
                return STATUS_NOT_CHECKED;
            }

            if (subscription.subscription_status === STATUS_CANCELLED) {
                return STATUS_CANCELLED;
            }

            return STATUS_PENDING;
        };

        this.status = getStatus();
        this.id = subscription.uuid;


        this.active = function () {
            var activeStatus = [STATUS_CHECKED, STATUS_NOT_CHECKED];
            if (activeStatus.indexOf(getStatus()) > -1)
                return true;
            else return false;
        };

        this.disable = function () {
            var disableStatus = [STATUS_CANCELLED, STATUS_PENDING];
            if (disableStatus.indexOf(getStatus()) > -1)
                return true;
            else return false;
        };

        var setToggleCallbacks = function () {
            if (toggleCallbacksInit === true) {
                return;
            }

            $.each(toggleStateCallbacks, function (i, callback) {
                attendance.addPostCheckoutCallback(function () {
                    callback(this);
                });
                attendance.addPostCheckinCallback(function () {
                    callback(this);
                });
            })
        };

        this.create_card_el = function (service_pk, created_by, checkin_button_msg, checkout_button_msg) {

            var header_color;
            var button_disabled = false;
            var button_text;
            var button_class_name;
            var status_text;
            var status_card_text;
            var tooltip_message;

            var button = $('<button>').addClass('btn btn-trans').css({
                'margin-top': '5px',
                'border-radius': '25px'

            });

            console.log('4. Status de inscrição do card: ' + subscription.attendance_status);

            setToggleCallbacks();

            switch (getStatus()) {
                case STATUS_CANCELLED:
                    header_color = COLOR_DISABLED;
                    button_text = 'Registrar entrada';
                    status_text = 'Cancelado';
                    status_card_text = 'CANCELADO';
                    tooltip_message = 'Inscrição cancelada';
                    button_class_name = 'default';
                    button_disabled = true;

                    break;
                case STATUS_CHECKED:
                    header_color = COLOR_CHECKED;
                    button_text = checkout_button_msg;
                    status_card_text = 'PRESENTE';
                    button_class_name = 'success';
                    status_text = 'Confirmado';
                    break;

                case STATUS_NOT_CHECKED:
                    header_color = COLOR_NOT_CHECKED;
                    button_text = checkin_button_msg;
                    status_card_text = 'AUSENTE';
                    button_class_name = 'success';
                    status_text = 'Confirmado';
                    break;
                case STATUS_PENDING:
                default:
                    header_color = COLOR_PENDING;
                    tooltip_message = 'Inscrição pendente';
                    button_text = 'Registrar entrada';
                    status_text = 'Pendente';
                    status_card_text = 'PENDENTE';
                    button_class_name = 'default';
                    button_disabled = true;
                    break;
            }

            button.addClass('btn-' + button_class_name);

            if (button_disabled) {
                button.attr('disabled', '');
            }

            button.text(button_text);


            var card_html = "<div class=\"panel attendance-card panel-card\">";
            card_html += "<div class=\"header-card container-fluid\" style=\"background-color:" + header_color + "\">";
            card_html += "<div class=\"row\" style=\"height: 40px;\">";
            card_html += "<div class=\"col-xs-6\">";
            card_html += "<h3 class=\"status-card\"style=\" ;\" >" + status_card_text + "</h3>";
            card_html += "</div>";
            card_html += "<div class=\"col-xs-3 col-xs-offset-3\">";
            card_html += "<div class=\"float-right time-circles\" style=\"width: 100%;height: 25px;\">";
            card_html += "</div>";
            card_html += "</div>";
            card_html += "</div>";
            card_html += "</div>";
            card_html += "<div class=\"row\">";
            card_html += "<div class=\"col-xs-6 col-xs-offset-3\" style=\"margin-top:-50px;\">";
            //card_html +=               "<img src=\"http://cdn.staticneo.com/w/evangelion/6/6a/Shinji.jpg\" class=\"img-responsive img-circle\" alt=\"Responsive image\">";
            card_html += "</div>";
            card_html += "</div>";
            card_html += "<div class=\"panel-body\">";
            card_html += "<h2 class=\"text-center text-bold\" style=\"font-size: 20px;padding-top: 10px\">" + subscription.name + "</h2>";
            card_html += "<div class=\"row\" style=\"padding-top: 8px\">";
            card_html += "<div class=\"col-md-7 text-center\">";
            card_html += "<h3 style=\"padding-bottom: 5px\">";
            card_html += "<i class=\"fas fa-barcode\" data-toggle=\"tooltip\" data-placement=\"left\" title=\"\" data-original-title=\"código da inscrição\"></i>";
            card_html += "<span> " + subscription.code + "</span>";
            card_html += "</h3>";
            card_html += "</div>";
            card_html += "<div class=\"col-md-5 text-center\">";
            card_html += "<h3 style=\" padding-bottom: 5px\">";
            card_html += "<i class=\"fas fa-list-ol\" data-toggle=\"tooltip\" title=\"\" data-original-title=\"Número da Inscrição\"></i>";
            card_html += "<span> " + subscription.event_count + "</span>";
            card_html += "</h3>";
            card_html += "</div>";
            card_html += "</div>";
            card_html += "<div class=\"row\" style=\"padding-top: 8px\">";
            card_html += "<div class=\"col-md-12\" style=\"overflow: hidden\">";
            card_html += "<div class=\"divider-card\"></div>";
            card_html += "<h3 class=\"secondary-informations\" >";
            card_html += "<i class=\"far fa-envelope\" data-toggle=\"tooltip\" title=\"\" data-original-title=\"Email\"></i>";
            card_html += "<span> " + subscription.email + "</span>";
            card_html += "</h3>";
            card_html += "<h3 class=\"secondary-informations\" >";
            card_html += "<i class=\"fas fa-th-list\" data-toggle=\"tooltip\" title=\"\" data-original-title=\"Categoria\"></i>";
            card_html += "<span> " + subscription.category_name + "</span>";
            card_html += "</h3>";
            card_html += "<h3 class=\"secondary-informations\" >";
            card_html += "<i class=\"fas fa-th-large\" data-toggle=\"tooltip\" title=\"\" data-original-title=\"Lote\"></i>";
            card_html += "<span> " + subscription.lot_name + "</span>";
            card_html += "</h3>";
            card_html += "<div style=\" text-align: center\">" + button.prop('outerHTML') + "<div>";
            card_html += "</div>";
            card_html += "</div>";
            card_html += "</div>";
            card_html += "</div>";

            card_el = $(card_html);

            if (!card_parent_el) {
                var status = getStatus();
                card_parent_el = $('<div>').addClass('col-md-' + card_size);
                if (status === STATUS_CANCELLED || status === STATUS_PENDING) {
                    card_parent_el.attr('data-toggle', 'tooltip');
                    card_parent_el.attr('title', '');
                    card_parent_el.attr('data-original-title', tooltip_message);

                }


            }

            card_parent_el.html(card_el);

            window.setTimeout(function () {
                var button = card_parent_el.find('button');
                switch (getStatus()) {
                    case STATUS_CHECKED:
                        button.on('click', function () {
                            console.log('0. trigger checkout.');

                            var button_text = button.text();
                            button.attr('disabled', '');
                            button.text('Aguarde...');
                            attendance.checkout(
                                service_pk,
                                subscription,
                                created_by
                            ).then(function () {
                                console.log('3. recriando card.');
                                self.create_card_el(service_pk, created_by, checkin_button_msg, checkout_button_msg);
                                button.removeAttr('disabled');
                                button.text(button_text);
                            });
                        });
                        break;

                    case STATUS_NOT_CHECKED:
                        button.on('click', function () {
                            console.log('0. trigger checkin.');
                            var button_text = button.text();
                            button.attr('disabled', '');
                            button.text('Aguarde...');
                            attendance.checkin(
                                service_pk,
                                subscription,
                                created_by
                            ).then(function () {
                                console.log('3. recriando card.');
                                self.create_card_el(service_pk, created_by, checkin_button_msg, checkout_button_msg);
                                button.removeAttr('disabled');
                                button.text(button_text);
                            });
                        });
                        break;
                }
            }, 300);
        };

        this.setSize = function (size) {
            card_size = size || 4;
        };

        this.getElement = function (service_pk, created_by, checkin_button_msg, checkout_button_msg) {
            self.create_card_el(service_pk, created_by, checkin_button_msg, checkout_button_msg);

            return card_parent_el;
        };

        this.toggle = function (service_pk, created_by, checkin_button_msg, checkout_button_msg) {
            return new Promise(function (resolve) {
                if (getStatus() === STATUS_CHECKED) {
                    attendance.checkout(service_pk, subscription, created_by).then(
                        function () {
                            self.create_card_el(service_pk, created_by, checkin_button_msg, checkout_button_msg);
                            resolve();
                        });
                }
                if (getStatus() === STATUS_NOT_CHECKED) {
                    console.log("Realizar Checkin");
                    attendance.checkin(service_pk, subscription, created_by).then(
                        function () {
                            self.create_card_el(service_pk, created_by, checkin_button_msg, checkout_button_msg);
                            resolve();
                        }
                    );
                }
            });
        };
    };

})(jQuery, window.cgsy.attendance);

// ==========================================================================//
// CARD LIST
// ==========================================================================//
(function ($, attendance) {

    attendance.List = function (service_pk, created_by) {
        var self = this;
        this.cards = [];

        this.addCard = function (card) {
            this.cards.push(card);
        };

        this.clear = function () {
            this.cards = [];
        };

        this.render = function (parent_el, checkin_button_msg, checkout_button_msg) {
            parent_el = $(parent_el);
            parent_el.html('');

            $.each(this.cards, function (i, card) {
                parent_el.append(card.getElement(service_pk, created_by, checkin_button_msg, checkout_button_msg));
            });
            this.clear();
        };
    };

})(jQuery, window.cgsy.attendance);

// ==========================================================================//
// TYPING SEARCH
// ==========================================================================//
// SEARCH
// --------------------------------------------------------------------------//
(function ($, attendance, SubscriptionCollection, Card) {
    attendance.Search = function (attendance, subscription_uri) {

        var collection = new SubscriptionCollection(subscription_uri);
        var card_size = 4;
        var preSearchCallback = function () {
        };
        var afterSearchCallback = function () {
        };
        var cardStateCallback = function (card) {
        };

        var createCard = function (subscription) {
            var card = new Card(subscription, attendance);
            card.setSize(card_size);
            card.addToggleStateCallback(function () {
                cardStateCallback(card);
            });
            return card;
        };

        this.setPreSearchCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            preSearchCallback = callback;
        };

        this.setAfterSearchCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            afterSearchCallback = callback;
        };

        this.setCardStateCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            cardStateCallback = callback;
        };

        this.fetch = function (search_criteria) {
            preSearchCallback();
            return new Promise(function (resolve) {
                collection.fetch(search_criteria).then(function (subscriptions) {
                    var cards = [];
                    $.each(subscriptions, function (i, subscription) {
                        cards.push(createCard(subscription));
                    });
                    resolve(cards);
                    afterSearchCallback();
                });
            });
        };

        this.setCardSize = function (size) {
            card_size = size || 4;
        };
    };
})(
    jQuery,
    window.cgsy.attendance,
    window.cgsy.attendance.SubscriptionCollection,
    window.cgsy.attendance.Card
);

// --------------------------------------------------------------------------//
// TYPING SEARCH
// --------------------------------------------------------------------------//
(function ($, attendance, List) {
    attendance.TypingSearch = function (search, service_pk, created_by, checkin_button_msg, checkout_button_msg) {
        var searchTimer = null;
        var cards_list = new List(service_pk, created_by);

        var fetch = function (search_criteria, list_el) {
            list_el = $(list_el);

            window.clearTimeout(searchTimer);
            searchTimer = window.setTimeout(function () {
                search.fetch(search_criteria).then(function (cards) {
                    cards_list.clear();
                    $.each(cards, function (i, card) {
                        cards_list.addCard(card);
                    });
                    cards_list.render(list_el, checkin_button_msg, checkout_button_msg);
                });
            }, 400);
        };

        this.watch = function (input_el, list_el) {
            $(document).on('keydown', function (event) {
                input_el.focus();

            });

            $(input_el).on('keyup', function () {
                var input = $(this);
                $(list_el).html('');
                fetch(input.val(), list_el);
            });
        };
    };
})(jQuery, window.cgsy.attendance, window.cgsy.attendance.List);

// --------------------------------------------------------------------------//
// PROCESSCOUNTER SEARCH
// --------------------------------------------------------------------------//
(function ($, attendance) {
    attendance.ProcessCounter = function () {

        var beginCounterCallback = [];
        var endCounterCallback = [];
        var self = this;
        var createTimeCirclesEl = function (el_output, ends_in) {
            var timeCirclesEl = "<div id=\"DateCountdown\" data-timer=\"" + ends_in + "\" style=\"font-size: 0 !important;\" ></div>";
            timeCirclesEl = $(timeCirclesEl);
            el_output.append(timeCirclesEl);

            $("#DateCountdown").TimeCircles({
                "animation": "smooth",
                "number_size": 0.01,
                "bg_width": 0.25,
                "fg_width": 0.055,
                "start_angle": 0,
                "circle_bg_color": "#FFFFFF",
                "time": {
                    "Days": {
                        "text": "Days",
                        "color": "#40484F",
                        "show": false
                    },
                    "Hours": {
                        "text": "Hours",
                        "color": "#40484F",
                        "show": false
                    },
                    "Minutes": {
                        "text": "Minutes",
                        "color": "#40484F",
                        "show": false
                    },
                    "Seconds": {
                        "text": "",
                        "color": "#FFFFFF",
                        "show": true
                    }
                }
            });

        };

        this.addBeginCounterCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            beginCounterCallback.push(callback);
        };
        this.addEndCounterCallback = function (callback) {
            if (typeof callback !== 'function') {
                console.error('Callback is not a function: ' + callback);
                return;
            }
            endCounterCallback.push(callback);
        };

        this.createCounter = function (el_output, ends_in, destroyInEnd) {

            $.each(beginCounterCallback, function (i, callback) {
                callback();
            });

            createTimeCirclesEl(el_output, ends_in);

            $("#DateCountdown").TimeCircles({count_past_zero: false})
                .addListener(function (unit, value, total) {
                    if (total <= 0) {
                        if (destroyInEnd === true) {
                            self.finalizeCounter()
                        }
                        else {
                            runEndCounterCallback();
                        }
                    }
                });
        };

        var runEndCounterCallback = function () {
            $.each(endCounterCallback, function (i, callback) {
                callback();
            });
        };

        this.finalizeCounter = function () {
            $("#DateCountdown").TimeCircles().destroy();
            runEndCounterCallback();
        };

        this.destroyCounter = function () {
            $("#DateCountdown").TimeCircles().destroy();
        };

        this.stopCounter = function () {
            $("#DateCountdown").TimeCircles().stop();
        };


    };
})(jQuery, window.cgsy.attendance);

// --------------------------------------------------------------------------//
// BARCODE SEARCH
// --------------------------------------------------------------------------//
(function ($, attendance, ProcessCounter) {
    attendance.BarcodeSearch = function (search, service_pk, created_by, checkin_button_msg, checkout_button_msg) {
        var searchTimer = null;
        var selected_card = null;
        var cleanTimer = null;

        var reset = function () {
            selected_card = null;
        };
        var processCounter = new ProcessCounter();


        var fetch = function (search_criteria, list_el, input_el) {
            list_el = $(list_el);
            input_el = $(input_el);

            window.clearTimeout(searchTimer);
            processCounter.destroyCounter();

            var createAttendanceSpaceEvent = function (unit, value, total) {
                $(document).on('keydown', function (event) {
                    list_el.focus();
                    if (event.keyCode === 32 && selected_card != null) {
                        checkinByToggle(selected_card, service_pk, created_by, input_el, checkin_button_msg, checkout_button_msg);
                        processCounter.destroyCounter().then(
                            function () {
                                processCounter.destroyCounter();
                            }
                        );
                    }
                })
            };
            searchTimer = window.setTimeout(function () {

                search.fetch(search_criteria).then(function (cards) {

                    if (!cards.length) {
                        reset();
                        return;
                    }
                    var card = cards[0];

                    var reread = selected_card && selected_card.id === card.id && card.active() === true;


                    if (reread === true) {
                        checkinByToggle(selected_card, service_pk, created_by, list_el, checkin_button_msg, checkout_button_msg).then(
                            function () {
                                processCounter.destroyCounter();
                            }
                        );
                        return;
                    }

                    selected_card = card;
                    var outputCard = selected_card.getElement(service_pk, created_by, checkin_button_msg, checkout_button_msg);
                    list_el.html(outputCard);

                    if (card.active() === true) {
                        processCounter.addBeginCounterCallback(createAttendanceSpaceEvent);
                        processCounter.addEndCounterCallback(function () {
                            list_el.html('');
                            selected_card = null;
                        });
                        processCounter.createCounter($(outputCard).find('.time-circles'), 60, true);
                    }
                });
            }, 400);

        };

        var checkinByToggle = function (card, service_pk, created_by, input_el, checkin_button_msg, checkout_button_msg) {
            return new Promise(function (resolve) {
                card.toggle(service_pk, created_by, checkin_button_msg, checkout_button_msg).then(function () {
                    card = null;
                    $(input_el).val('');
                });
            });

        };

        var preventDefaultScanner = function (input_el) {
            input_el = $(input_el);
            input_el.val('');
            $(document).on('keydown', function (event) {
                input_el.focus();
                if (event.keyCode === 13 || event.keyCode === 74) {
                    event.preventDefault();
                }

            });
        };

        this.watch = function (input_el, list_el) {
            input_el = $(input_el);
            preventDefaultScanner(input_el);
            input_el.focus();
            input_el.on('keyup', function () {
                if (input_el.val().length === 8) {
                    window.clearTimeout(cleanTimer);
                    fetch(input_el.val(), list_el, input_el);
                    window.setTimeout(function () {
                        input_el.val('');
                    }, 400);

                }

            });
        };

        window.setTimeout(function () {
            search.setCardStateCallback(function () {
                reset();
                processCounter.destroyCounter();
            });
        }, 200);
    };
})(jQuery, window.cgsy.attendance, window.cgsy.attendance.ProcessCounter);

// --------------------------------------------------------------------------//
// QRCODE SEARCH
// --------------------------------------------------------------------------//
(function ($, attendance) {
    attendance.QrcodeSearch = function (search, service_pk, created_by) {
        var searchTimer = null;

        var fetch = function (search_criteria, result_el) {

        };

        this.start = function () {
        };

        this.stop = function () {
        };
    };
})(jQuery, window.cgsy.attendance);


function createTypingSearch(options) {
    var attendance = new window.cgsy.attendance.Attendance(
        options['checkinUri'],
        options['success_checkin_msg'],
        options['fail_checkin_msg'],
        options['checkoutUri'],
        options['success_checkout_msg'],
        options['fail_checkout_msg']
    );

    var search = new window.cgsy.attendance.Search(
        attendance,
        options['subscriptionUri']
    );
    search.setPreSearchCallback(function () {
        console.log('set some loader');
    });
    search.setAfterSearchCallback(function () {
        console.log('hide loader');
    });

    var typingSearch = new window.cgsy.attendance.TypingSearch(
        search,
        options['servicePk'],
        options['createdBy'],
        options['checkin_button_msg'],
        options['checkout_button_msg']
    );
    typingSearch.watch($(options['inputEl']), $(options['listEl']));
}

function createBarCodeSearch(options) {
    var attendance = new window.cgsy.attendance.Attendance(
        options['checkinUri'],
        options['success_checkin_msg'],
        options['fail_checkin_msg'],
        options['checkoutUri'],
        options['success_checkout_msg'],
        options['fail_checkout_msg']
    );

    var search = new window.cgsy.attendance.Search(
        attendance,
        options['subscriptionUri']
    );
    search.setCardSize(12);

    var barCodeSearch = new window.cgsy.attendance.BarcodeSearch(
        search,
        options['servicePk'],
        options['createdBy'],
        options['checkin_button_msg'],
        options['checkout_button_msg']
    );
    $(options['inputEl']).focus();
    barCodeSearch.watch($(options['inputEl']), $(options['listEl']));
}