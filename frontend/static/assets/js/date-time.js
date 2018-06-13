//Código Js que cria os elementos da data e do tempo, além de setar a data
// mínima de finalização do evento a data de inicio dele

// #datepicker-begin .datapicker
// #datepicker-end  .datapicker

function createDateStartDateEnd(path_start, path_end) {

    $(path_start).datetimepicker({
        locale: 'pt-br',
        format: 'DD/MM/YYYY',
        allowInputToggle: true,
        defaultDate: new Date(),
        minDate: new Date()

    }).on('dp.change', function (e) {
        $(path_end).data("DateTimePicker").minDate(e.date)
    });

    $(path_end).datetimepicker({
        locale: 'pt-br',
        format: 'DD/MM/YYYY',
        allowInputToggle: true,
        defaultDate: new Date(),
        minDate: new Date()
    });

}

function createTimePicker() {
    $('.timepicker').datetimepicker({
        locale: 'pt-br',
        format: 'HH:mm',
        allowInputToggle: true,
        defaultDate: new Date(),
        minDate: new Date()
    });
}

function createDatePicker() {
        $('.datapicker').datetimepicker({
        locale: 'pt-br',
        format: 'DD/MM/YYYY',
        allowInputToggle: true,
        defaultDate: new Date(),
        minDate: new Date()
    });
}