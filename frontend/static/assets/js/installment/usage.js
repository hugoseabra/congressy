//================================= BASE ======================================
/**
 * Resgata collection de contratos.
 * @param {string} subscription_pk
 * @returns {Promise}
 */
function fetchContracts(subscription_pk) {
    var collection = new window.cgsy.installment.collections.ContractCollection(subscription_pk);

    return new Promise(function (resolve, reject) {
        collection.fetch().then(function () {
            if (!collection.isValid()) {
                return reject('Erro ao resgatar contratos.');
            }
            resolve(collection);
        }).catch(function (reason) {
            console.error(reason);
            reject(reason);
        });
    });
}

/**
 * Resgata lista de Parcelas de contrato.
 * @param {cgsy.installment.models.Contract} contract
 * @returns {Promise}
 */
function fetchContractParts(contract) {
    return new Promise(function (resolve, reject) {
        contract.fetchParts().then(function () {
            resolve(contract.part_collection.items);
        }).catch(function (reason) {
            console.error(reason);
            reject(reason);
        });
    });
}

function getContractForm(subscription_pk, limit_date_str, base_day, amount) {
    var form_el = $('#contract-form').clone();
        form_el.removeAttr('id');

    var modal_el = $('#generic-modal').clone();
        modal_el.removeAttr('id');

    var button_el = $('.submit-button', modal_el);
    var num_parts_field_el = $('[name=num_installments]', form_el);
    var expiration_day_field_el = $('[name=expiration_day]', form_el);

    var parts_list_el = $('.contract-part-table', form_el);

    var form_modal = new window.cgsy.installment.component.ContractFormModal(
        subscription_pk,
        modal_el,
        form_el,
        button_el
    );
    form_modal.setEl('expiration-day-field', expiration_day_field_el);
    form_modal.setEl('num-installments-field', num_parts_field_el);
    form_modal.setEl('part-table-list', parts_list_el);

    form_modal.populate({
        'expiration_day': parseInt(base_day),
        'amount': (amount < 0) ? -(amount) : amount,
        'minimum_amount': 25,
        'limit_date_str': limit_date_str
    });

    form_modal.open();
}

//================================ DOM ========================================
function renderPartsList(contract, parent_el) {
    parent_el = $(parent_el);

    var table = new window.cgsy.installment.component.PartTable(parent_el, contract);
    table.setEl('cancel-button', $('#cancel-installment-contract'));

    fetchContractParts(contract).then(function (parts) {
        parts.forEach(function (part) {
            table.addItem(part);
        });
        table.render();

    }).catch(function (reason) {
        console.error(reason);
    });
}

function getContracts(sub_pk) {
    fetchContracts(sub_pk).then(function (contract_collection) {
        var opens = contract_collection.items.filter(function (item) {
            return item.get('status') === 'open';
        });

        var list_parent_el = $('#constract-parts-list');
        if (opens.length === 0) {
            var table = new window.cgsy.installment.component.PartTable(list_parent_el);
                table.render();
            return;
        }
        var open_contract = opens[0];

        renderPartsList(open_contract, list_parent_el);

    }).catch(function (reason) {
        console.error('Erro ao buscar contratos.', reason);
    })
}
