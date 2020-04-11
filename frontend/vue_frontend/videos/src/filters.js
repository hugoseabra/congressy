import Vue from "vue/dist/vue.js"; // See note about import below

/** Vue Filters Start */
Vue.filter('truncate', function (text, length, suffix) {
    if (text && text.length > length) {
        return text.substring(0, length) + suffix;
    } else {
        return text;
    }
});
/** Vue Filters End */