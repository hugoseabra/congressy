//================================= BASE ======================================
/**
 * Resgata collection de contratos.
 * @param {string} subscription_pk
 * @returns {Promise}
 */
function getContracts(subscription_pk) {
    var collection = new window.cgsy.installment.collections.ContractCollection(subscription_pk);

    return new Promise(function (resolve, reject) {
        collection.fetch().then(function () {
            if (!collection.isValid()) {
                return reject('Erro ao resgatar contratos.');
            }
            resolve(collection);
        }).catch(function(reason) {
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
function getContractParts(contract) {
    return new Promise(function (resolve, reject) {
        contract.fetchParts().then(function () {
            resolve(contract.part_collection.items);
        }).catch(function (reason) {
            console.error(reason);
            reject(reason);
        });
    });
}

//================================ DOM ========================================
function renderPartsList(contract, parent_el) {
    parent_el = $(parent_el);

    var table = new window.cgsy.installment.component.PartTable(parent_el);

    getContractParts(contract).then(function (parts) {
        var counter = 0;
        parts.forEach(function (part) {
            table.addItem(part);
            // table.addItem({
            //     '#': part.get('installment_number'),
            //     'amount': 'R$ ' + as_currency(part.get('amount')),
            //     'exp_date': part.get('expiration_date').format('DD/MM/YYYYY'),
            //     'paid': part.get('paid') === true,
            //     'next-part': part.get('paid') === false && counter === 0
            // });
            // if (part.get('paid') === false) {
            //     counter++;
            // }
        });

        table.render();
    }).catch(function(reason) {
        console.error(reason);
    });
}


$(document).ready(function () {
    getContracts('4198685d-fb60-40c5-b740-81127ed76828').then(function (contracts) {
        var opens = contracts.items.filter(function (item) {
            return item.get('status') === 'open';
        });
        if (opens.length === 0) {
            return;
        }

        var open_contract = opens[0];

        renderPartsList(open_contract, $('#constract-parts-list'));
    }).catch(function() {
        console.error('Erro ao buscar contratos.');
    })
});