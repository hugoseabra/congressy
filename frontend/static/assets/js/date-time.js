//Código Js que cria os elementos da data e do tempo, além de setar a data
// mínima de finalização do evento a data de inicio dele

// #datepicker-begin .datapicker
// #datepicker-end  .datapicker

var minDate = new Date();
    minDate.setHours(0, 0, 0, 0);

var tooltips = {
    today: 'Ir para hoje',
    clear: 'Limpar seleção',
    close: 'Feche o seletor',
    selectMonth: 'Selecione o mês',
    prevMonth: 'Mês anterior',
    nextMonth: 'Próximo mês',
    selectYear: 'Selecione o ano',
    prevYear: 'Ano anterior',
    nextYear: 'Próximo ano',
    selectDecade: 'Selecione Década',
    prevDecade: 'Década anterior',
    nextDecade: 'Próxima Década',
    prevCentury: 'Século Anterior',
    nextCentury: 'Próximo Século',
    incrementHour: 'Incremente a hora',
    pickHour: 'Selecione a Hora',
    decrementHour: 'Decremente a Hora',
    incrementMinute: 'Incremente a Hora',
    pickMinute: 'Selecione o Minuto',
    decrementMinute: 'Decremente o Minuto',
    incrementSecond: 'Incremente o Segundo',
    pickSecond: 'Selecione o Segundo',
    decrementSecond: 'Decremente o Segundo'
};

function createDateStartDateEnd(path_start, path_end) {

    var date_end = createDatePicker(path_end);

    var date_start = createDatePicker(path_start).on('dp.change', function (e) {
        date_end.data("DateTimePicker").minDate(e.date);
    });

}

function createTimePicker(el) {
    if (!el) {
        el = '.timepicker';
    }
    el = $(el);
    el.datetimepicker({
        locale: 'pt-br',
        format: 'HH:mm',
        allowInputToggle: true,
        tooltips: tooltips,
    });
    return el
}

function createDatePicker(el) {
    if (!el) {
        el = '.datapicker';
    }
    el = $(el);
    el.datetimepicker({
        locale: 'pt-br',
        format: 'DD/MM/YYYY',
        allowInputToggle: true,
        minDate: minDate,
        tooltips: tooltips,
        showTodayButton: true

    });

    return el;
}