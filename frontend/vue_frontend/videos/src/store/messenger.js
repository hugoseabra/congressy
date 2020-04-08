import Vue from "vue/dist/vue.js"; // See note about import below
import Vuex from "vuex";

import Category from "../model/category"
import CategoryCollection from "../model/category_collection"

Vue.use(Vuex);
Vue.config.productionTip = false;

let messenger = new Vuex.Store({
    mutations: {
        addSuccess(state, msg) {
            state.msgs['success'].push(msg);
        },
        addWarning(state, msg) {
            state.msgs['warning'].push(msg);
        },
        addInfo(state, msg) {
            state.msgs['info'].push(msg);
        },
        addError(state, msg) {
            state.msgs['error'].push(msg);
        },
        triggerLoader(state, msg) {
            if (state.loader) {
                return;
            }
            state.loader = Messenger().run({
                hideAfter: 50000, // long time. Loader will wait to be finished.
                progressMessage: msg,
                action: function () {} // action will persist notification.
            });
        },
        hideLoader(state) {
            if (!state.loader) {
                return;
            }
            const m = state.loader;
            state.loader = null;
            m.cancel();
        },
        trigger(state, payload) {
            const top_bottom = payload && payload.hasOwnProperty('top') in payload && payload['top'] === true ? 'top' : 'bottom';
            const left_right = payload && payload.hasOwnProperty('left') && payload['left'] === true ? 'left' : 'right';

            Messenger.options = {
                extraClasses: 'messenger-fixed messenger-on-'+ top_bottom +' messenger-on-' + left_right,
                theme: 'flat'
            };
            Object.keys(state.msgs).forEach((type) => {
                state.msgs[type].forEach((msg) => {
                    let data = {
                        type: type,
                        message: msg,
                        showCloseButton: true,
                        hideAfter: 10
                    };
                    Messenger().post(data);
                });
                state.msgs[type] = [];
            });
        }
    },
    actions: {
        addSuccess (context) {
            context.commit('addSuccess');
        },
        addWarning (context) {
            context.commit('addWarning');
        },
        addInfo (context) {
            context.commit('addInfo');
        },
        addError (context) {
            context.commit('addError');
        },
        trigger (context) {
            context.commit('add');
        }
    },
    state: {
        'loader': null,
        'msgs': {
            'success': [],
            'warning': [],
            'info': [],
            'error': [],
        }
    },
    strict: process.env.NODE_ENV !== "production",
});

export default {
    messenger,
    install(Vue) { //resetting the default store to use this
        Vue.prototype.$messenger = messenger;
    }
};