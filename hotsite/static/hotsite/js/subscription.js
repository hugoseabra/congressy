$(document).ready(function () {
    $('#id_phone').mask("(99) 99999-9999");
    $('#id_cpf').mask("999.999.999-99");

    var institution_cnpj = $('#id_institution_cnpj');
    if (institution_cnpj.length) {
        console.log('a');
        institution_cnpj.mask("99.999.999/9999-99");
    }

    var city_el = $('#id_city_name');

    $('#id_state').change(function () {
        city_el.empty();

        var that = $(this);
        window.setTimeout(function () {
            city_el.append($('<option>').text('Carregando...'));
            fetch_cities($(that));
        }, 500);
    });

    city_el.change(function () {
        $("#id_city").val($(this).val());
    });

    $('#id_zip_code').on('keyup', function () {
        searchByCep();
    });
});


function fetch_cities(uf_el, selected_value, callback) {
    uf_el = $(uf_el);
    selected_value = selected_value || '';
    callback = callback || null;

    var city_el = $('#id_city_name');
    $.ajax({
        url: "/api/cities/?uf=" + $(uf_el).val() + '&length=1000', success: function (result) {

            var listitems = [];
            var ids = [];

            $.each(result.results, function (key, value) {
                listitems.push('<option value=' + value.id + '>' + value.name + '</option>');
                ids.push(value.id)
            });

            if (selected_value) {
                window.setTimeout(function() {
                    city_el.val(selected_value);
                    $("#id_city").val(selected_value);
                }, 500);
            } else {
                $("#id_city").val(ids[0]);
            }

            city_el.html(listitems.join(''));
            city_el.prop('disabled', false);

            if (callback) {
                console.log(result.results);
                callback(result.results)
            }
        }
    });


}
