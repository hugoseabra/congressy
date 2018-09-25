function next_page(form_id) {
    
    var form = document.getElementById(form_id);

    var wizard_next_btn_el = $('.wizard_next_btn');
    var wizard_next_loader_el = $('.wizard_next_loader');

    if (form_is_valid(form)) {
        wizard_next_btn_el.hide();
        wizard_next_loader_el.show();
        $('#' + form_id).submit()
    } else {
        alert('Existem alguns campos obrigatórios não preenchidos!');
    }


}


function form_is_valid(form_el) {

    for (var i = 0; i < form_el.elements.length; i++) {
        if (form_el.elements[i].value === '' && form_el.elements[i].hasAttribute('required')) {
            return false;
        }
    }

    return true;

}

