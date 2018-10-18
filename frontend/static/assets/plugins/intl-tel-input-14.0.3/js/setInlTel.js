function createPhoneInput(phoneIdEl, ddiEl, pathUtils) {
    ddiEl = $(ddiEl);
    var phone = $(phoneIdEl);
    var inputPhone = document.querySelector(phoneIdEl);
    var initialDdi;
    if (ddiEl.val() === '') {
        initialDdi = 'br';
        phone.mask("(99) 99999-9999");
    }
    else {
        initialDdi = ddiEl.val().toLowerCase()
        phone.unmask();
    }


    var intTelEl = window.intlTelInput(inputPhone, {
        initialCountry: initialDdi,
        preferredCountries: ['us', 'br'],
        utilsScript: pathUtils
    });

    phone.on("countrychange", function () {
        var ddi = intTelEl.getSelectedCountryData()['iso2'];
        if (ddi === 'br') {
            phone.mask("(99) 99999-9999");
        }
        else {
            phone.unmask();
        }

    });


    phone.mask("(99) 99999-9999");
    phone.on('change blur', function () {
        if (phone.val().trim()) {
            ddiEl.val(intTelEl.getSelectedCountryData()['iso2'].toUpperCase());
        }
    });
    ddiEl.removeAttr('required');

}