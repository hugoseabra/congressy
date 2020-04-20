import Vue from "vue/dist/vue.js"; // See note about import below
import Vuex from "vuex";

import Project from "../model/project"

Vue.use(Vuex);
Vue.config.productionTip = false;

let project_store = new Vuex.Store({
    mutations: {
        setAsProcessing(state) {
            state.processing = true;
        },
        setAsNotProcessing(state) {
            state.processing = false;
        },
        updateItem(state, data) {
            if (!data) return;
            Object.assign(state.item, data);
        },
        updateCover(state, video_pk) {
            if (!video_pk) return;
            Object.assign(state.item, { 'main_video': video_pk });
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
            Object.assign(state.item, new Project().toData());
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
        fetch({state, commit}) {
            this._vm.$messenger.commit('triggerLoader', 'aguarde...');
            this.commit('setAsProcessing');

            return new Promise((resolve) => {
                const item = new Project();
                item.populate(state.item);
                item.fetch().then(() => {
                    resolve();
                    commit('updateItem', item.toData());

                    this._vm.$messenger.commit('hideLoader');
                    this.commit('setAsNotProcessing');

                }).catch(reason => {
                    if (reason.hasOwnProperty('stack')) {
                        console.error(reason.stack);
                    }
                    this._vm.$messenger.commit('addError', reason.message);
                    this._vm.$messenger.commit('trigger');
                });
            });
        },
        save({state}) {
            this.dispatch('runBeforeHooks');

            const item = new Project();
            item.populate(state.item);

            this._vm.$messenger.commit('triggerLoader', 'aguarde...');
            this.commit('setAsProcessing');

            item.save().then(() => {
                this._vm.$messenger.commit('addSuccess', 'Projeto salvo com sucesso.');
                this._vm.$messenger.commit('trigger');

                this._vm.$messenger.commit('hideLoader');
                this.commit('setAsNotProcessing');

                this.commit('updateItem', item.toData());

            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');
            });
        },
        saveCover({state}) {
            this.dispatch('runBeforeHooks');

            const item = new Project();
            item.populate(state.item);

            this._vm.$messenger.commit('triggerLoader', 'aguarde...');
            this.commit('setAsProcessing');

            item.save().then(() => {
                this._vm.$messenger.commit('addSuccess', 'Video de capa definido.');
                this._vm.$messenger.commit('trigger');

                this._vm.$messenger.commit('hideLoader');
                this.commit('setAsNotProcessing');

                this.commit('updateItem', item.toData());

            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');
            });
        },
        remove({state}) {
            this.dispatch('runBeforeHooks');

            const item = new Project();
            item.populate(state.item);

            this._vm.$messenger.commit('triggerLoader', 'aguarde...');
            this.commit('setAsProcessing');

            item.delete().then(() => {
                this._vm.$messenger.commit('addSuccess', 'Projeto excluído com sucesso.');
                this._vm.$messenger.commit('trigger');

                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('trigger');
                this.commit('setAsNotProcessing');

            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }

                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');

                this.commit('setAsNotProcessing');
            });
        }
    },
    state: {
        'item': new Project().toData(),
        'processing': false,
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
    project_store,
    install(Vue) { //resetting the default store to use this
        Vue.prototype.$project_store = project_store;
    }
};