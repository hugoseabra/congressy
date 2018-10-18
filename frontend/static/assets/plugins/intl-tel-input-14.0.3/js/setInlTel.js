function createPhoneInput(pathUtils) {


    var inputPhone = document.querySelector('#id_person-phone');
    var initialDdi;
    if ($('#id_person-ddi').val() === '') {
        initialDdi = 'br';
    }
    else {
        initialDdi = $('#id_person-ddi').val().toLowerCase()
    }


    var intTelEl = window.intlTelInput(inputPhone, {
        initialCountry: initialDdi,
        preferredCountries: ['us', 'br'],
        utilsScript: pathUtils
    });

    var phone = $('#id_person-phone');

    phone.on('change blur', function () {
        if (phone.val().trim()) {
            $('#id_person-ddi').val(intTelEl.getSelectedCountryData()['iso2'].toUpperCase());
        }
    });
    $('#id_person-ddi').removeAttr('required');

}