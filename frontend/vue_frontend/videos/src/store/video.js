import Vue from "vue/dist/vue.js"; // See note about import below
import Vuex from "vuex";
import Video from "../model/video";
import VideoCollection from "../model/video_collection";

Vue.use(Vuex);
Vue.config.productionTip = false;

const collection = new VideoCollection();

let video_store = new Vuex.Store({
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
            Object.assign(state.item, new Video().toData());
        },
        removeItemInCollection(state) {
            collection.reset();

            state.items.forEach((i) => {
                if (state.item.pk === i.pk) {
                    return;
                }
                const item = new Video();
                item.populate(i);
                collection.add(item);
            });

            this.commit('updateItems');
            this.commit('resetItem');
        },
        setPlayer(state, {provider, link}) {
            state.player_provider = provider;
            state.player_link = link;
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
        fetchCollection({state, commit}) {
            this.dispatch('runBeforeHooks');

            if (state.processing) {
                setTimeout(() => this.dispatch('fetchCollection'), 2000);
                return;
            }

            this._vm.$messenger.commit('triggerLoader', 'aguarde...');
            this.commit('setAsProcessing');

            collection.fetch().then(() => {
                commit('updateItems');

                this.commit('setAsNotProcessing');
                this._vm.$messenger.commit('hideLoader');

            }).catch((reason) => {
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');

                this.commit('setAsNotProcessing');
            });
        },
        save({state, commit}) {
            this.dispatch('runBeforeHooks');

            if (state.processing) {
                setTimeout(() => this.dispatch('save'), 2000);
                return;
            }

            const item = new Video();
            item.populate(state.item);

            this._vm.$messenger.commit('triggerLoader', 'aguarde...');

            this.commit('setAsProcessing');

            item.save().then(() => {
                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('addSuccess', 'Video salvo com sucesso.');
                this._vm.$messenger.commit('trigger');

                commit('updateItem', item.toData());
                setTimeout(() => this.dispatch('fetchCollection'), 200);

                this.commit('setAsNotProcessing');

            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }
                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');

                this.commit('setAsNotProcessing');
                this.dispatch('runAfterHooks');
            });
        },
        saveByLink({state, commit}, link) {
            this.dispatch('runBeforeHooks');

            if (state.processing) {
                setTimeout(() => this.dispatch('saveByLink'), 2000);
                return;
            }

            const item = new Video();

            this._vm.$messenger.commit('triggerLoader', 'aguarde...');

            item.saveByLink(link).then(() => {
                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('addSuccess', 'Video salvo com sucesso.');
                this._vm.$messenger.commit('trigger');

                commit('updateItem', item.toData());
                setTimeout(() => this.dispatch('fetchCollection'), 200);

            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }
                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');
                this.dispatch('runAfterHooks');
            });
        },
        remove({state, commit}) {
            this.dispatch('runBeforeHooks');

            const item = new Video();
            item.populate(state.item);

            this._vm.$messenger.commit('triggerLoader', 'aguarde...');

            item.delete().then(() => {
                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('addSuccess', 'Vídeo excluído com sucesso.');
                this._vm.$messenger.commit('trigger');

                commit('removeItemInCollection');
                setTimeout(() => this.dispatch('fetchCollection'), 200);

            }).catch((reason) => {
                if (reason.hasOwnProperty('stack')) {
                    console.error(reason.stack);
                }
                this._vm.$messenger.commit('hideLoader');
                this._vm.$messenger.commit('addError', reason.message);
                this._vm.$messenger.commit('trigger');
                this.dispatch('runAfterHooks');
            });
        }
    },
    state: {
        'items': [],
        'item': new Video().toData(),
        'player_link': null,
        'player_provider': null,
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
    video_store,
    install(Vue) { //resetting the default store to use this
        Vue.prototype.$video_store = video_store;
    }
};