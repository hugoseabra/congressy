function maskFromPlaceholder(placeholder) {
    if (!placeholder) {
        return null;
    }
    var mask = '';
    $.each(placeholder.split(''), function(i, n) {
        if (/^-?[\d.]+(?:e-?\d+)?$/.test(n)){ n = '9'; }
        mask += n;
    });
    return mask;
}

function createPhoneInput(phoneIdEl, ddiEl, pathUtils) {
    ddiEl = $(ddiEl);
    var phone = $(phoneIdEl);
    var inputPhone = document.querySelector(phoneIdEl);
    var initialDdi, placeholder;
    if (ddiEl.val() === '') {
        initialDdi = 'br';
        phone.mask("(99) 99999-9999");
    }
    else {
        initialDdi = ddiEl.val().toLowerCase();
        phone.unmask();

        placeholder = phone.attr('placeholder');
        console.log(placeholder);
        if (placeholder) {
            phone.mask(maskFromPlaceholder(placeholder));
        }
    }


    var intTelEl = window.intlTelInput(inputPhone, {
        initialCountry: initialDdi,
        preferredCountries: ['us', 'br'],
        utilsScript: pathUtils
    });

    phone.on("countrychange", function () {
        var ddi = intTelEl.getSelectedCountryData()['iso2'];
            phone.unmask();

        if (ddi === 'br') {
            phone.mask("(99) 99999-9999");
        } else {
            placeholder = phone.attr('placeholder');
            if (placeholder) {
                var mask = maskFromPlaceholder(placeholder);
                phone.mask(mask);
            }
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