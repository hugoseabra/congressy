function loadPredefinedEvents() {
    window.setTimeout(function () {
        $('[data-field-name=input-number]').addClass('numbers-only');

        $('.numbers-only').on('input', function () {
            this.value = this.value.replace(/[^0-9+-\/.]/g, '').replace(/(\..*)\./g, '$1');
        });
    }, 300);
    app.createFileUploadEvents();
}

$(document).ready(function () {
    loadPredefinedEvents();
});
