var suggestionEngine = new Bloodhound({
    datumTokenizer: function (datum) {
        return Bloodhound.tokenizers.whitespace(datum.value);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: '/api/cities/?q=%QUERY',
        wildcard: '%QUERY',
        filter: function (main_json) {
            return $.map(main_json.results, function (result) {
                return {
                    value: result.name + '-' + result.uf,
                    city_id: result.id
                };
            });
        }
    }
});

$('#city .typeahead').typeahead(null, {
    name: 'cities',
    display: 'value',
    source: suggestionEngine,
    limit: 10
});

$('#city .typeahead').on('typeahead:selected', function (e, datum) {
    $("#id_city").val(datum.city_id);
});

$(document).ready(function () {
    $('#id_phone').mask("(99) 9 9999-9999");
    $('#id_cpf').mask("999.999.999-99");

    $('#id_zip_code').on('keyup', function () {
        searchByCep();
    });
});
