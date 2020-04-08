import Vue from "vue/dist/vue.js"; // See note about import below
import Vuex from "vuex";

import Category from "../model/category"
import CategoryCollection from "../model/category_collection"

Vue.use(Vuex);
Vue.config.productionTip = false;

const collection = new CategoryCollection();

let category_store = new Vuex.Store({
    mutations: {
        updateItem(state, data) {
            if (!data) return;
            Object.assign(state.item, data);
        },
        updateItems(state) {
            this.dispatch('runBeforeHooks');

            state.items.length = 0;
            collection.items.forEach(item => state.items.push(item.toData()));

            this.dispatch('runAfterHooks');
        },
        updateItemInCollection(state) {
            let update = false;
            state.items.forEach((item) => {
                if (state.item.pk === item.pk) {
                    Object.assign(item, state.item);
                    update = true;
                }
            });
            if (update === false) {
                state.items.push(state.item)
            }

            this.commit('updateItems');
        },
        selectItem(state, pk) {
            if (!pk) return;

            state.items.forEach((item) => {
                if (item.pk === pk) {
                    this.commit('updateItem', item);
                }
            });
        },
        resetItem(state) {
            Object.assign(state.item, new Category().toData());
        },
        removeItemInCollection(state) {
            collection.reset();

            state.items.forEach((i) => {
                if (state.item.pk === i.pk) {
                    return;
                }
                const item = new Category();
                item.populate(i);
                collection.add(item);
            });

            this.commit('updateItems');
            this.commit('resetItem');
        },
        addHook(state, {type, id, callback}) {
            if (callback instanceof Function) {
                state.hooks[type]['items'][id] = callback;
            }
        }
    },
    actions: {
        runBeforeHooks({state}) {
            Object.values(state.hooks['before']['items']).forEach(callback => callback());
        },
        runAfterHooks({state}) {
            Object.values(state.hooks['after']['items']).forEach(callback => callback());
        },
        fetchCollection({commit}) {
            this.dispatch('runBeforeHooks');

            collection.fetch().then(() => {
                commit('updateItems');
            }).catch((reason) => {
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');
            });
        },
        save({state}) {
            this.dispatch('runBeforeHooks');

            const item = new Category();
            item.populate(state.item);

            item.save().then(() => {
                this._vm.$messenger.commit('addSuccess', 'Categoria salva com sucesso.');
                this._vm.$messenger.commit('trigger');

                this.commit('updateItem', item.toData());
                setTimeout(() => this.dispatch('fetchCollection'), 200);

            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');
            });
        },
        remove({state, commit}) {
            this.dispatch('runBeforeHooks');

            const item = new Category();
            item.populate(state.item);

            item.delete().then(() => {
                this._vm.$messenger.commit('addSuccess', 'Categoria excluída com sucesso.');
                this._vm.$messenger.commit('trigger');

                commit('removeItemInCollection');
            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }

                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');
            });
        }
    },
    state: {
        'items': [],
        'item': new Category().toData(),
        'hooks': {
            'before': {
                'items': [],
            },
            'after': {
                'items': [],
            }
        }
    },
    strict: process.env.NODE_ENV !== "production",
});

export default {
    category_store,
    install(Vue) { //resetting the default store to use this
        Vue.prototype.$category_store = category_store;
    }
};