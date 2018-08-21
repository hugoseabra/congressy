window.cgsy = window.cgsy || {};

(function ($, cgsy) {

    /**
     * PriceCalculator - calcula preços a partir de um percentual (em decimal)
     * informado.
     *
     * @param {number} cgsy_percent - Percentual Congressy em Decimal
     * @param {number} transfer_tax - Se a taxa residual será transferida ao
     * participate, resultando em um cálculo de preços diferente, interpretando
     * o preço cheio/bruto como 100%.
     *
     * @constructor
     */
    cgsy.PriceCalculator = function(cgsy_percent, transfer_tax) {
        cgsy_percent = parseFloat(cgsy_percent);
        transfer_tax = transfer_tax === true;

        /**
         * Recupera preço bruto a partir de um preço líquido.
         * @param {number} liquid_price - Preço líquido em decimal
         * @returns {object} - float
         */
        this.getPrice = function(liquid_price) {
            liquid_price = parseFloat(liquid_price);

            var result;
            if (transfer_tax === true) {
                result = liquid_price + (liquid_price * cgsy_percent);
            } else {
                var full_proportion = (100 - (cgsy_percent * 100)) / 100;
                result = ((liquid_price * 100) / full_proportion) / 100;
            }

            return parseFloat(result).toFixed(2);
        };

        /**
         * Recupera preço líquido a partir de um preço bruto.
         * @param {number} full_price - Preço bruto em decimal
         * @returns {object} - float
         */
        this.getLiquidPrice = function(full_price) {
            full_price = parseFloat(full_price);

            var result;
            if (transfer_tax === true) {
                var full_proportion = 1 + cgsy_percent;
                result = (full_price * 100) / (full_proportion * 100);
            } else {
                result = full_price - (full_price * cgsy_percent);
            }

            return parseFloat(result).toFixed(2);
        };
    };

})(jQuery, window.cgsy);