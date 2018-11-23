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
    table.setEl('cancel-button', $('#cancel-installment-contract'));

    getContractParts(contract).then(function (parts) {
        parts.forEach(function (part) {
            table.addItem(part);
        });

        table.render();

    }).catch(function (reason) {
        console.error(reason);
    });
}

function getContracts(sub_pk) {
    fetchContracts(sub_pk).then(function (contracts) {
        var opens = contracts.items.filter(function (item) {
            return item.get('status') === 'open';
        });
        if (opens.length === 0) {
            return;
        }
        var open_contract = opens[0];

        renderPartsList(open_contract, $('#constract-parts-list'));

    }).catch(function (reason) {
        console.error('Erro ao buscar contratos.', reason);
    })
}
