function update_publishing_state(state, url) {


    var sender = new cgsy.AjaxSender(url);
    sender.setSuccessCallback(function () {
        location.reload();
    });

    sender.setFailCallback(function (res) {
        console.error(res.statusText);
        location.reload();
    });

    sender.send('POST', {'state': state});

}
