<template>
    <div>
        <div v-if="items.length > 0">
            <category-list v-show="loading === false" :items="items"/>
        </div>
        <div v-else-if="loading === false">
            <div class="text-center" style="height: 100px;margin-top:50px">
                <small class="text-muted">Nenhum registro</small>
                <hr />
                <div><button class="btn btn-sm btn-success">Criar categoria</button></div>
            </div>
        </div>
        <div v-show="loading === true" style="border:1px dashed #ddd;">
            <div class="text-center" style="height: 100px;margin-top:50px">
                <i class="fas fa-circle-notch text-muted fa-spin fa-4x"></i>
            </div>
        </div>
    </div>
</template>

<script>
    import CategoryList from "./CategoryList";

    export default {
        name: 'CategoryGrid',
        components: {CategoryList},
        data() {
            return {
                'loading': true,
                'items': this.$category_store.state.items,
            }
        },
        mounted() {
            this.$category_store.commit('addHook', {
                'type': 'before',
                'id': 'category.grid.load',
                'callback': () => {
                    this.loading = true;
                }
            });
            this.$category_store.commit('addHook', {
                'type': 'after',
                'id': 'category.grid.load',
                'callback': () => this.loading = false
            });
            this.$category_store.dispatch('fetchCollection');
        }
    }
</script>