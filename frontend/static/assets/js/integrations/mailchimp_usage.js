window.integrations.Config = {
    'mailchimp_form_url': null
};

function mailchimp_reload_form(reset) {
    var target_el = $('#mailchimp-form');

    if (reset === true) {
        var loader = new window.integrations.Loader(target_el);
        loader.show();
    }

    var url = window.integrations.Config.mailchimp_form_url;
    var form = new window.integrations.MailchimpForm(url, target_el);
        form.load();
}


function mailchimp_show_config(button_el, row) {
    if (row.isOpened()) {
        button_el.addClass('btn-trans');
        row.close();
    } else {
        button_el.removeClass('btn-trans');
        row.open();
        mailchimp_reload_form(true);
    }
}

$(document).ready(function() {
    var mailchimp_row = new window.integrations.MailchimpRow($('#mailchimp-form-block'));

    $('#mailchimp-config-button').click(function(el) {
        mailchimp_show_config($(this), mailchimp_row);
    });
});