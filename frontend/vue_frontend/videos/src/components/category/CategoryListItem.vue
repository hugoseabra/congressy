<template>
    <tr>
        <td>
            <input type="checkbox" @change="updateItem" :checked="active === true" name="active" style="display:none" class="js-switch" :id="'cat_id_'+item.pk">
        </td>
        <td>
            <a href="javascript:void(0)" @click="openForm">{{ item.name }}</a>
        </td>
        <td class="text-center hidden-xs">{{ item.num_videos }}</td>
        <td>
            <div class="btn-group">
                <button type="button"
                        class="btn btn-primary btn-trans btn-sm dropdown-toggle"
                        data-toggle="dropdown"
                        aria-expanded="true">
                    <span class="fas fa-cog"></span>
                </button>
                <ul class="dropdown-menu dropdown-menu-right"
                    role="menu">
                    <li>
                        <a href="javascript:void(0)" @click="openForm">
                            <i class="fas fa-pencil-alt"></i>
                            Editar
                        </a>
                    </li>

                    <li v-if="!item.num_videos">
                        <a href="javascript:void(0)" @click="removeItem">
                            <i class="fas fa-trash-alt"> </i>
                            Excluir
                        </a>
                    </li>
                </ul>
            </div>
        </td>
    </tr>
</template>

<script>
    export default {
        name: 'CategoryListItem',
        props: {
            item: {
                type: Object,
                required: true,
            },
        },
        data() {
            return {
                'active': this.item.active
            }
        },
        methods: {
            selectItem() {
                this.$category_store.commit('selectItem', this.item.pk);
            },
            openForm() {
                this.selectItem();
                window.jQuery('#category-form-modal').modal();
            },
            updateItem() {
                this.active = !this.active;
                this.selectItem();
                this.$category_store.commit('updateItem', {
                    'active': this.active
                });
                this.$category_store.dispatch('save');
            },
            removeItem() {
                if (confirm(`Deseja realmente excluir a categoria "${this.item.name}"?`)) {
                    this.selectItem();
                    this.$category_store.dispatch('remove');
                }
            }
        },
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
